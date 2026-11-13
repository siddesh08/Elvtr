#!/usr/bin/env python3
"""Prepare one ticket for review.

Routing runs at the same time as retrieval, prompt construction, and the LLM
call. A routing result does not decide whether retrieval or the LLM runs.
process_ticket follows the Homework 6 workflow contract. trace_id stays null
until Task 6 adds tracing.
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTING_SERVICE_PATH = REPO_ROOT / "assignment6" / "task2" / "routing_service.py"
RETRIEVAL_SERVICE_PATH = REPO_ROOT / "assignment6" / "task3" / "retrieval_service.py"
LLM_SERVICE_PATH = REPO_ROOT / "assignment6" / "task4" / "llm_service.py"

# Homework 5 generation settings and the ticket-summary schema from Homework 4.
MODEL = "qwen2.5:1.5b-instruct-q4_K_M"
STREAM = False
GENERATION_OPTIONS = {"temperature": 0, "seed": 42, "num_predict": 512}
SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "customer_request": {"type": "string"},
        "missing_information": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["summary", "customer_request", "missing_information"],
    "additionalProperties": False,
}
SUMMARY_FIELDS = ("summary", "customer_request", "missing_information")
RETRIEVAL_COUNT = 5
RECORD_FIELDS = ("rank", "chunk_id", "distance", "content", "metadata")
DEPARTMENTS = (
    "Billing and Payments",
    "Customer Service",
    "General Inquiry",
    "Human Resources",
    "IT Support",
    "Product Support",
    "Returns and Exchanges",
    "Sales and Pre-Sales",
    "Service Outages and Maintenance",
    "Technical Support",
)

# Iteration 2, with one paragraph changed so the ticket body and the retrieved
# articles stay distinct. Summary and customer_request stay on the ticket body.
# Evidence may inform missing_information.
INSTRUCTIONS = """You write an internal note for a human support agent about one support ticket. You do not route the ticket, invent a fix, or take an action.

The text under TICKET BODY is the customer's message. The text under RETRIEVED EVIDENCE is external support context, not part of the ticket. Use the ticket body for summary and customer_request. If a detail is not in the ticket body, do not add it to those two fields. Retrieved evidence may inform missing_information.

Reply with a JSON object and nothing else. The object has exactly these fields:
- summary: one or two sentences describing the reported issue.
- customer_request: the specific action or reply the customer asked the agent for. If the body asks for a meeting, a timeline, steps, a warranty or repair policy, or answers to listed questions, include those asks. Do not replace them with a general description of the topic.
- missing_information: a list of details needed to understand or act on the request. Use an empty list when nothing is clearly missing.
"""


class WorkflowFailure(Exception):
    """A service or a response check failed. The message is safe to return."""


def _load_symbol(path: Path, module_name: str, symbol: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{symbol} could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    value = getattr(module, symbol, None)
    if value is None:
        raise RuntimeError(f"{symbol} could not be loaded.")
    return value


RoutingService = _load_symbol(ROUTING_SERVICE_PATH, "homework6_routing_service", "RoutingService")
RetrievalService = _load_symbol(
    RETRIEVAL_SERVICE_PATH,
    "homework6_retrieval_service",
    "RetrievalService",
)
LLMClient = _load_symbol(LLM_SERVICE_PATH, "homework6_llm_service", "LLMClient")


class TicketWorkflow:
    """Route a ticket and summarize it from the ticket body plus retrieved evidence."""

    def __init__(
        self,
        routing_service: Any | None = None,
        retrieval_service: Any | None = None,
        llm_service: Any | None = None,
    ) -> None:
        self.routing_service = routing_service if routing_service is not None else RoutingService()
        self.retrieval_service = (
            retrieval_service if retrieval_service is not None else RetrievalService()
        )
        self.llm_service = llm_service if llm_service is not None else LLMClient()

    def process_ticket(self, request: object) -> dict[str, Any]:
        """Validate one ticket, then run routing and summarization in parallel."""
        workflow_record_id = str(uuid4())
        if not isinstance(request, dict):
            return _rejected(workflow_record_id, None, "request must be a dictionary.")

        ticket_id, identifier_error = _ticket_id(request)
        body, body_error = _body(request)
        if identifier_error or body_error:
            return _rejected(
                workflow_record_id,
                ticket_id,
                _join(identifier_error, body_error),
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both before waiting, so routing does not gate summarization.
            routing_future = executor.submit(self._run_routing, body)
            summary_future = executor.submit(self._run_summarization, body)
            routing_result, routing_error = _outcome(routing_future)
            summary_result, summary_error = _outcome(summary_future)

        if routing_error or summary_error:
            return _failed(
                workflow_record_id,
                ticket_id,
                _join(routing_error, summary_error),
            )

        department, class_scores = routing_result
        evidence, summary = summary_result
        return {
            "ticket_id": ticket_id,
            "workflow_record_id": workflow_record_id,
            "terminal_status": "summary_ready_for_review",
            "recommended_department": department,
            "class_scores": class_scores,
            "ticket_body": body,
            "ticket_summary": summary,
            "retrieved_evidence": evidence,
            "trace_id": None,
            "error": None,
        }

    def _run_routing(self, body: str) -> tuple[str, dict[str, Any]]:
        try:
            response = self.routing_service.route_ticket({"ticket_body": body})
        except WorkflowFailure:
            raise
        except Exception as error:
            raise WorkflowFailure("Routing service failed.") from error
        return _validated_routing(response)

    def _run_summarization(self, body: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        try:
            response = self.retrieval_service.retrieve_evidence({"ticket_body": body})
        except WorkflowFailure:
            raise
        except Exception as error:
            raise WorkflowFailure("Retrieval service failed.") from error
        evidence = _validated_evidence(response)
        try:
            prompt = _prompt(body, evidence)
        except WorkflowFailure:
            raise
        except Exception as error:
            raise WorkflowFailure("Prompt construction failed.") from error
        llm_request = {
            "prompt": prompt,
            "model": MODEL,
            "stream": STREAM,
            "options": dict(GENERATION_OPTIONS),
            "format": SUMMARY_SCHEMA,
        }
        try:
            llm_response = self.llm_service.call_llm(llm_request)
        except WorkflowFailure:
            raise
        except Exception as error:
            raise WorkflowFailure("LLM service failed.") from error
        return evidence, _validated_summary(llm_response)


def _ticket_id(request: dict) -> tuple[int | None, str | None]:
    if "ticket_id" not in request:
        return None, "ticket_id is required."
    value = request["ticket_id"]
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return None, "ticket_id must be a positive integer."
    return value, None


def _body(request: dict) -> tuple[str | None, str | None]:
    if "Body" not in request:
        return None, "Body is required."
    value = request["Body"]
    if not isinstance(value, str):
        return None, "Body must be a string."
    if not value.strip():
        return None, "Body must contain non-whitespace text."
    return value, None


def _join(first: str | None, second: str | None) -> str:
    parts = [part for part in (first, second) if part]
    return " ".join(parts)


def _rejected(workflow_record_id: str, ticket_id: int | None, error: str) -> dict[str, Any]:
    return _incomplete(workflow_record_id, ticket_id, "input_rejected", error)


def _failed(workflow_record_id: str, ticket_id: int | None, error: str) -> dict[str, Any]:
    return _incomplete(workflow_record_id, ticket_id, "workflow_failed", error)


def _incomplete(
    workflow_record_id: str,
    ticket_id: int | None,
    status: str,
    error: str,
) -> dict[str, Any]:
    return {
        "ticket_id": ticket_id,
        "workflow_record_id": workflow_record_id,
        "terminal_status": status,
        "recommended_department": None,
        "class_scores": None,
        "ticket_body": None,
        "ticket_summary": None,
        "retrieved_evidence": [],
        "trace_id": None,
        "error": error,
    }


def _outcome(future) -> tuple[Any, str | None]:
    try:
        return future.result(), None
    except WorkflowFailure as error:
        return None, str(error)
    except Exception:
        return None, "Workflow operation failed."


def _validated_routing(response: object) -> tuple[str, dict[str, Any]]:
    if not isinstance(response, dict) or set(response) != {"recommended_department", "class_scores"}:
        raise WorkflowFailure("Routing response did not match the contract.")
    department = response["recommended_department"]
    scores = response["class_scores"]
    if not isinstance(department, str) or str(department) not in DEPARTMENTS:
        raise WorkflowFailure("Routing response did not match the contract.")
    if (
        not isinstance(scores, dict)
        or len(scores) != len(DEPARTMENTS)
        or {str(name) for name in scores} != set(DEPARTMENTS)
    ):
        raise WorkflowFailure("Routing response did not match the contract.")

    class_scores: dict[str, Any] = {}
    for name, score in scores.items():
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
            raise WorkflowFailure("Routing response did not match the contract.")
        class_scores[str(name)] = score
    department = str(department)
    if any(score > class_scores[department] for score in class_scores.values()):
        raise WorkflowFailure("Routing response did not match the contract.")
    return department, class_scores


def _validated_evidence(response: object) -> list[dict[str, Any]]:
    if not isinstance(response, dict) or set(response) != {"evidence"}:
        raise WorkflowFailure("Retrieval response did not match the contract.")
    records = response["evidence"]
    if not isinstance(records, list) or len(records) != RETRIEVAL_COUNT:
        raise WorkflowFailure("Retrieval response did not match the contract.")

    evidence = []
    for expected_rank, record in enumerate(records, start=1):
        if not isinstance(record, dict) or set(record) != set(RECORD_FIELDS):
            raise WorkflowFailure("Retrieval response did not match the contract.")
        chunk_id = record["chunk_id"]
        content = record["content"]
        metadata = record["metadata"]
        if (
            record["rank"] != expected_rank
            or isinstance(record["rank"], bool)
            or not isinstance(record["rank"], int)
            or not isinstance(chunk_id, str)
            or not str(chunk_id)
            or not isinstance(content, str)
            or isinstance(record["distance"], bool)
            or not isinstance(record["distance"], (int, float))
            or not math.isfinite(record["distance"])
            or not isinstance(metadata, dict)
        ):
            raise WorkflowFailure("Retrieval response did not match the contract.")
        article_id = metadata.get("article_id")
        title = metadata.get("title")
        section = metadata.get("section")
        position = metadata.get("chunk_position")
        if (
            not isinstance(article_id, str)
            or not article_id.strip()
            or not isinstance(title, str)
            or not title.strip()
            or not isinstance(section, str)
            or not section.strip()
            or isinstance(position, bool)
            or not isinstance(position, int)
        ):
            raise WorkflowFailure("Retrieval response did not match the contract.")
        kept = dict(metadata)
        kept["article_id"] = str(article_id)
        kept["title"] = str(title)
        kept["section"] = str(section)
        evidence.append(
            {
                "rank": record["rank"],
                "chunk_id": str(chunk_id),
                "distance": record["distance"],
                "content": str(content),
                "metadata": kept,
            }
        )
    return evidence


def _prompt(body: str, evidence: list[dict[str, Any]]) -> str:
    passages = []
    for record in evidence:
        passages.append(
            f"[{record['rank']}] chunk_id: {record['chunk_id']}\n"
            f"title: {record['metadata']['title']}\n"
            f"{record['content']}"
        )
    evidence_text = "\n\n".join(passages)
    return (
        f"{INSTRUCTIONS}\n"
        "TICKET BODY\n"
        "The following text is the customer's message.\n"
        f"{body}\n\n"
        "RETRIEVED EVIDENCE\n"
        "The following passages are external support articles. "
        "They are not the customer's message.\n\n"
        f"{evidence_text}"
    )


def _validated_summary(response: object) -> dict[str, Any]:
    if not isinstance(response, dict) or set(response) != {"content"}:
        raise WorkflowFailure("LLM response did not match the contract.")
    content = response["content"]
    if not isinstance(content, str) or not content.strip():
        raise WorkflowFailure("LLM response did not match the contract.")
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as error:
        raise WorkflowFailure("Ticket summary did not match the contract.") from error
    if not isinstance(payload, dict) or set(payload) != set(SUMMARY_FIELDS):
        raise WorkflowFailure("Ticket summary did not match the contract.")

    summary = payload["summary"]
    customer_request = payload["customer_request"]
    gaps = payload["missing_information"]
    if not isinstance(summary, str) or not summary.strip():
        raise WorkflowFailure("Ticket summary did not match the contract.")
    if not isinstance(customer_request, str) or not customer_request.strip():
        raise WorkflowFailure("Ticket summary did not match the contract.")
    if not isinstance(gaps, list) or not all(isinstance(item, str) for item in gaps):
        raise WorkflowFailure("Ticket summary did not match the contract.")
    if any(not item.strip() for item in gaps):
        raise WorkflowFailure("Ticket summary did not match the contract.")
    sentences = _sentence_count(summary)
    if sentences < 1 or sentences > 2:
        raise WorkflowFailure("Ticket summary did not match the contract.")
    return {
        "summary": summary.strip(),
        "customer_request": customer_request.strip(),
        "missing_information": [item.strip() for item in gaps],
    }


def _sentence_count(text: str) -> int:
    pieces = re.findall(r"[^.!?]+[.!?]+|[^.!?]+$", text.strip())
    return sum(1 for piece in pieces if piece.strip())
