#!/usr/bin/env python3
"""Submit Homework 2 ticket 28763 to the deployed workflow."""

from __future__ import annotations

import csv
import json
import math
import unittest
import urllib.request
from pathlib import Path
from uuid import UUID

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = (
    REPO_ROOT
    / "assignment2"
    / "homework_materials"
    / "SIDDESH NATESAN - support_tickets - SIDDESH NATESAN - support_tickets.csv"
)
RESULT_PATH = Path(__file__).resolve().parent / "ticket_28763_result.json"
WORKFLOW_URL = "http://localhost:8000/tickets/process"
TICKET_ID = 28763
REQUEST_TIMEOUT_SECONDS = 300

RESULT_KEYS = (
    "ticket_id",
    "workflow_record_id",
    "terminal_status",
    "recommended_department",
    "class_scores",
    "ticket_body",
    "ticket_summary",
    "retrieved_evidence",
    "trace_id",
    "error",
)
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
SUMMARY_FIELDS = ("summary", "customer_request", "missing_information")
EVIDENCE_FIELDS = ("rank", "chunk_id", "distance", "content", "metadata")


def _ticket_body() -> str:
    with DATASET_PATH.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["ticket_id"] == str(TICKET_ID):
                return row["Body"]
    raise AssertionError(f"ticket {TICKET_ID} is not in the canonical dataset")


def _post(payload: dict) -> dict:
    encoded = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        WORKFLOW_URL,
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _finite_number(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
    )


class DeploymentTest(unittest.TestCase):
    def test_ticket_28763_matches_workflow_contract(self) -> None:
        body = _ticket_body()
        submitted = {"ticket_id": TICKET_ID, "Body": body}
        result = _post(submitted)
        RESULT_PATH.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        self.assertEqual(set(result), set(RESULT_KEYS))
        self.assertEqual(result["ticket_body"], submitted["Body"])
        self.assertEqual(result["ticket_id"], TICKET_ID)
        self.assertEqual(result["terminal_status"], "summary_ready_for_review")
        self.assertIsNone(result["error"])
        UUID(result["workflow_record_id"])
        self.assertIsInstance(result["trace_id"], str)
        self.assertTrue(result["trace_id"].strip())

        department = result["recommended_department"]
        self.assertIn(department, DEPARTMENTS)
        scores = result["class_scores"]
        self.assertEqual(set(scores), set(DEPARTMENTS))
        self.assertTrue(all(_finite_number(score) for score in scores.values()))
        self.assertEqual(scores[department], max(scores.values()))

        summary = result["ticket_summary"]
        self.assertEqual(set(summary), set(SUMMARY_FIELDS))
        self.assertIsInstance(summary["summary"], str)
        self.assertTrue(summary["summary"].strip())
        self.assertIsInstance(summary["customer_request"], str)
        self.assertTrue(summary["customer_request"].strip())
        self.assertIsInstance(summary["missing_information"], list)
        self.assertTrue(all(isinstance(item, str) and item.strip() for item in summary["missing_information"]))

        evidence = result["retrieved_evidence"]
        self.assertEqual(len(evidence), 5)
        for rank, record in enumerate(evidence, start=1):
            self.assertEqual(set(record), set(EVIDENCE_FIELDS))
            self.assertEqual(record["rank"], rank)
            self.assertIsInstance(record["chunk_id"], str)
            self.assertTrue(record["chunk_id"].strip())
            self.assertTrue(_finite_number(record["distance"]))
            self.assertIsInstance(record["content"], str)
            metadata = record["metadata"]
            self.assertIsInstance(metadata["article_id"], str)
            self.assertTrue(metadata["article_id"].strip())
            self.assertIsInstance(metadata["title"], str)
            self.assertTrue(metadata["title"].strip())
            self.assertIsInstance(metadata["section"], str)
            self.assertTrue(metadata["section"].strip())
            self.assertIsInstance(metadata["chunk_position"], int)
            self.assertNotIsInstance(metadata["chunk_position"], bool)


if __name__ == "__main__":
    unittest.main()
