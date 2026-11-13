"""HTTP API for the Homework 6 routing service."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi import FastAPI


def _load_routing_service_class():
    """Load RoutingService from the Homework 6 module path copied under /app."""
    path = Path(__file__).resolve().parent / "assignment6" / "task2" / "routing_service.py"
    spec = importlib.util.spec_from_file_location("homework6_routing_service", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Routing service could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    service_cls = getattr(module, "RoutingService", None)
    if service_cls is None:
        raise RuntimeError("Routing service could not be loaded.")
    return service_cls


RoutingService = _load_routing_service_class()
routing_service = RoutingService()

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/route")
def route(request: dict[str, object]) -> dict[str, object]:
    return routing_service.route_ticket(request)
