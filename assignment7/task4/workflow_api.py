"""HTTP API for the Homework 6 ticket workflow."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi import FastAPI


def _load_workflow_class():
    """Load TicketWorkflow from the Homework 6 module copied under /app."""
    path = Path(__file__).resolve().parent / "assignment6" / "task6" / "workflow.py"
    spec = importlib.util.spec_from_file_location("homework6_workflow", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Workflow could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    workflow_cls = getattr(module, "TicketWorkflow", None)
    if workflow_cls is None:
        raise RuntimeError("Workflow could not be loaded.")
    return workflow_cls


TicketWorkflow = _load_workflow_class()
workflow = TicketWorkflow()

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tickets/process")
def process_ticket(request: dict[str, object]) -> dict[str, object]:
    return workflow.process_ticket(request)
