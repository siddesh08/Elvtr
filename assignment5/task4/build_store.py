#!/usr/bin/env python3
"""Build the Homework 5 vector store from the Task 3 records.

The supplied VectorStore class does the embedding and the cosine search.
This file only loads the prepared records, builds the persisted table, and
opens that same table for a later query. It does not chunk articles.

Re-run from the repository root:

    .venv/bin/python assignment5/task4/build_store.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RECORDS_PATH = ROOT.parent / "task3" / "records.json"
MATERIALS = ROOT.parent / "homework_materials"
# LanceDB keeps the table at this path. A later run can query it without build().
STORE_PATH = ROOT / "homework5_vector_store"

# The setup guide imports VectorStore by module name from the materials folder.
sys.path.insert(0, str(MATERIALS))
from VectorStore import VectorStore

REQUIRED_FIELDS = ("chunk_id", "embedding_text", "content", "metadata")


def load_records(path: Path = RECORDS_PATH) -> list[dict]:
    """Read the Task 3 JSON. The records are already chunked."""
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        raise ValueError(f"{path} did not contain records")
    for record in records:
        missing = [field for field in REQUIRED_FIELDS if field not in record]
        if missing:
            raise ValueError(f"{record.get('chunk_id', '?')} is missing {missing}")
    chunk_ids = [record["chunk_id"] for record in records]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("chunk ids are not unique")
    return records


def open_store(database_path: Path = STORE_PATH) -> VectorStore:
    """Open the persisted store. Does not embed or replace the table."""
    return VectorStore(database_path)


def build_store(
    database_path: Path = STORE_PATH,
    records_path: Path = RECORDS_PATH,
) -> VectorStore:
    """Embed the Task 3 records and replace the LanceDB table."""
    records = load_records(records_path)
    store = VectorStore(database_path)
    store.build(records)
    return store


def query(
    ticket_body: str,
    top_k: int = 5,
    database_path: Path = STORE_PATH,
) -> list[dict]:
    """Embed an unaltered ticket body and return the ranked chunks."""
    return open_store(database_path).query(ticket_body, top_k=top_k)


def main() -> None:
    records = load_records()
    store = VectorStore(STORE_PATH)
    store.build(records)
    # A second instance reads the table that build() just wrote.
    reopened = VectorStore(STORE_PATH)
    check = reopened.query("Canon PIXMA MG3620 streaks and blotches", top_k=1)
    print(f"records: {len(records)}")
    print(f"store: {STORE_PATH}")
    print(f"reopen check: {check[0]['chunk_id']}")


if __name__ == "__main__":
    main()
