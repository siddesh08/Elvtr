#!/usr/bin/env python3
"""Ask the local course model for one structured ticket summary.

The model, schema, temperature, and seed stay fixed for later prompt
comparisons. Only the instruction text is meant to change.
Re-run from the repository root:

    .venv/bin/python assignment4/task5/summarize_ticket.py
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
SOURCE_CSV = (
    ROOT.parent.parent
    / "assignment3"
    / "homework_materials"
    / "SIDDESH NATESAN - support_tickets - SIDDESH NATESAN - support_tickets.csv"
)
OUTPUT_JSON = ROOT / "outputs" / "ticket_5572.json"

# Fixed for Homework 4. Do not swap the model or the generation settings.
MODEL = "qwen2.5:1.5b-instruct-q4_K_M"
API_URL = "http://localhost:11434/api/chat"
TEMPERATURE = 0
SEED = 42
TEST_TICKET_ID = 5572

# Initial prompt. The user message is the raw ticket body, unchanged.
INSTRUCTIONS = """You write an internal note for a human support agent about one support ticket. You do not route the ticket, invent a fix, or take an action.

The user message is the ticket body. Use only that text. If a detail is not in the body, do not add it.

Reply with a JSON object and nothing else. The object has exactly these fields:
- summary: one or two sentences describing the reported issue.
- customer_request: the action or outcome the customer appears to want.
- missing_information: a list of details needed to understand or act on the request. Use an empty list when nothing is clearly missing.
"""

OUTPUT_SCHEMA = {
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

REQUIRED_FIELDS = ("summary", "customer_request", "missing_information")
SENTENCE_BREAK = re.compile(r"[^.!?]+[.!?]+|[^.!?]+$")


def _sentence_count(text: str) -> int:
    return sum(1 for piece in SENTENCE_BREAK.findall(text.strip()) if piece.strip())


def validate_summary(payload: object) -> dict:
    """Reject anything that is not the Task 5 object."""
    if not isinstance(payload, dict):
        raise ValueError("model output is not a JSON object")
    extra = set(payload) - set(REQUIRED_FIELDS)
    missing = set(REQUIRED_FIELDS) - set(payload)
    if extra or missing:
        raise ValueError(f"fields must be exactly {list(REQUIRED_FIELDS)}")

    summary = payload["summary"]
    request = payload["customer_request"]
    gaps = payload["missing_information"]
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("summary must be a non-empty string")
    if not isinstance(request, str) or not request.strip():
        raise ValueError("customer_request must be a non-empty string")
    if not isinstance(gaps, list) or not all(isinstance(item, str) for item in gaps):
        raise ValueError("missing_information must be a list of strings")
    if any(not item.strip() for item in gaps):
        raise ValueError("missing_information contains an empty string")

    sentences = _sentence_count(summary)
    if sentences < 1 or sentences > 2:
        raise ValueError(f"summary has {sentences} sentences, expected 1 or 2")
    return {
        "summary": summary.strip(),
        "customer_request": request.strip(),
        "missing_information": [item.strip() for item in gaps],
    }


def summarize_ticket(body: str) -> dict:
    """Send one raw ticket body and return the validated summary."""
    if not isinstance(body, str) or not body.strip():
        raise ValueError("ticket body is empty")

    request_body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": body},
        ],
        "format": OUTPUT_SCHEMA,
        "stream": False,
        "options": {"temperature": TEMPERATURE, "seed": SEED},
    }
    encoded = json.dumps(request_body).encode("utf-8")
    http_request = urllib.request.Request(
        API_URL,
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(http_request, timeout=180) as response:
            raw = json.load(response)
    except urllib.error.URLError as error:
        raise RuntimeError(f"Ollama request failed: {error}") from error

    content = raw.get("message", {}).get("content", "")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("model returned an empty message")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(f"model content is not JSON: {content}") from error
    return validate_summary(parsed)


def load_body(ticket_id: int) -> str:
    source = pd.read_csv(SOURCE_CSV, dtype=str, usecols=["ticket_id", "Body"])
    match = source.loc[source["ticket_id"] == str(ticket_id), "Body"]
    if len(match) != 1:
        raise SystemExit(f"ticket {ticket_id} not found once in the source CSV")
    body = match.iloc[0]
    if not isinstance(body, str) or not body.strip():
        raise SystemExit(f"ticket {ticket_id} has an empty body")
    return body


def main() -> None:
    body = load_body(TEST_TICKET_ID)
    summary = summarize_ticket(body)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"ticket_id: {TEST_TICKET_ID}")
    print(json.dumps(summary, indent=2))
    print(f"wrote {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
