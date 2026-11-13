#!/usr/bin/env python3
"""Retrieve evidence for one ticket body from the Homework 5 vector store.

The persisted LanceDB store is opened once and reused. The retrieval count is
5, from the Homework 5 evaluation. retrieve_evidence follows
assignment6/task1/retrieval_contract.md. This module does not rebuild the index.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from typing import Any

# assignment6/task3/retrieval_service.py -> repository root is parents[2].
REPO_ROOT = Path(__file__).resolve().parents[2]
VECTOR_STORE_PATH = REPO_ROOT / "assignment5" / "homework_materials" / "VectorStore.py"
DEFAULT_DATABASE_PATH = REPO_ROOT / "assignment5" / "task4" / "homework5_vector_store"

# Homework 5 precision was 0.520 at k = 5 and 0.360 at k = 10.
RETRIEVAL_COUNT = 5
RECORD_FIELDS = ("rank", "chunk_id", "distance", "content", "metadata")


def _load_vector_store_class():
    """Import the supplied VectorStore without putting it on sys.path."""
    if not VECTOR_STORE_PATH.is_file():
        raise RuntimeError("Retrieval vector store could not be opened.")
    spec = importlib.util.spec_from_file_location("homework5_vector_store", VECTOR_STORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Retrieval vector store could not be opened.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    store_cls = getattr(module, "VectorStore", None)
    table_name = getattr(module, "TABLE_NAME", None)
    if store_cls is None or not isinstance(table_name, str):
        raise RuntimeError("Retrieval vector store could not be opened.")
    return store_cls, table_name


class RetrievalService:
    """Validate a ticket body and return the stored top-k chunks."""

    def __init__(self, database_path: str | Path | None = None) -> None:
        path = Path(database_path) if database_path is not None else DEFAULT_DATABASE_PATH
        self.retrieval_count = RETRIEVAL_COUNT
        try:
            store_cls, table_name = _load_vector_store_class()
            table_dir = path / f"{table_name}.lance"
            if not table_dir.is_dir():
                raise RuntimeError("Retrieval vector store could not be opened.")
            self._store = store_cls(path)
            self._store._database.open_table(table_name)
        except RuntimeError:
            raise
        except Exception as error:
            raise RuntimeError("Retrieval vector store could not be opened.") from error

    def retrieve_evidence(self, request: object) -> dict[str, list[dict[str, Any]]]:
        """Search once. Raises on invalid input or a retrieval failure."""
        ticket_body = _ticket_body(request)
        try:
            matches = self._store.query(ticket_body, top_k=self.retrieval_count)
        except Exception as error:
            raise RuntimeError("Retrieval query failed.") from error
        return {"evidence": _evidence(matches, self.retrieval_count)}


def _ticket_body(request: object) -> str:
    if not isinstance(request, dict):
        raise ValueError("request must be a dictionary.")
    if "ticket_body" not in request:
        raise ValueError("ticket_body is required.")
    ticket_body = request["ticket_body"]
    if not isinstance(ticket_body, str):
        raise ValueError("ticket_body must be a string.")
    if not ticket_body.strip():
        raise ValueError("ticket_body must contain non-whitespace text.")
    return ticket_body


def _plain_text(value: object) -> str | None:
    if not isinstance(value, str) or isinstance(value, bytes):
        return None
    text = str(value)
    if not text:
        return None
    return text


def _finite_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value)


def _integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _metadata(value: object) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    article_id = _plain_text(value.get("article_id"))
    title = _plain_text(value.get("title"))
    section = _plain_text(value.get("section"))
    position = value.get("chunk_position")
    if article_id is None or title is None or section is None or not _integer(position):
        return None
    metadata = dict(value)
    metadata["article_id"] = article_id
    metadata["title"] = title
    metadata["section"] = section
    metadata["chunk_position"] = position
    return metadata


def _evidence(matches: object, count: int) -> list[dict[str, Any]]:
    if not isinstance(matches, list) or len(matches) != count:
        raise RuntimeError("Retrieval result does not match the contract.")

    evidence = []
    for expected_rank, record in enumerate(matches, start=1):
        if not isinstance(record, dict) or set(record) != set(RECORD_FIELDS):
            raise RuntimeError("Retrieval result does not match the contract.")
        chunk_id = _plain_text(record["chunk_id"])
        content = record["content"]
        metadata = _metadata(record["metadata"])
        if (
            record["rank"] != expected_rank
            or not _integer(record["rank"])
            or chunk_id is None
            or not isinstance(content, str)
            or not _finite_number(record["distance"])
            or metadata is None
        ):
            raise RuntimeError("Retrieval result does not match the contract.")
        evidence.append(
            {
                "rank": record["rank"],
                "chunk_id": chunk_id,
                "distance": record["distance"],
                "content": content,
                "metadata": metadata,
            }
        )
    return evidence
