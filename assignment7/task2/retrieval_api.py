"""HTTP API for the Homework 6 retrieval service."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi import FastAPI


def _load_retrieval_service_class():
    """Load RetrievalService from the Homework 6 module path copied under /app."""
    path = Path(__file__).resolve().parent / "assignment6" / "task3" / "retrieval_service.py"
    spec = importlib.util.spec_from_file_location("homework6_retrieval_service", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Retrieval service could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    service_cls = getattr(module, "RetrievalService", None)
    if service_cls is None:
        raise RuntimeError("Retrieval service could not be loaded.")
    return service_cls


RetrievalService = _load_retrieval_service_class()
retrieval_service = RetrievalService()

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/search")
def search(request: dict[str, object]) -> dict[str, object]:
    return retrieval_service.retrieve_evidence(request)
