#!/usr/bin/env python3
"""Route one ticket body with the Homework 4 classifier.

The classifier is the Homework 3 router that Homework 4 kept: the Homework 2
cleaner, word TF-IDF, and logistic regression with C=1.0. It is loaded once
and reused. route_ticket follows assignment6/task1/routing_contract.md.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from typing import Any

# assignment6/task2/routing_service.py -> repository root is parents[2].
REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER_PATH = REPO_ROOT / "assignment3" / "task2" / "ticket_router.py"
DEFAULT_MODEL_PATH = REPO_ROOT / "assignment3" / "task2" / "outputs" / "ticket_router.joblib"

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
RESPONSE_FIELDS = ("recommended_department", "class_scores")


def _load_ticket_router_class():
    """Import the Homework 3 TicketRouter without putting it on sys.path."""
    if not ROUTER_PATH.is_file():
        raise RuntimeError("Routing classifier code could not be loaded.")
    spec = importlib.util.spec_from_file_location("homework3_ticket_router", ROUTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Routing classifier code could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    router_cls = getattr(module, "TicketRouter", None)
    if router_cls is None:
        raise RuntimeError("Routing classifier code could not be loaded.")
    return router_cls


class RoutingService:
    """Validate a ticket body and return the saved classifier's route."""

    def __init__(self, model_path: str | Path | None = None) -> None:
        path = Path(model_path) if model_path is not None else DEFAULT_MODEL_PATH
        try:
            router_cls = _load_ticket_router_class()
            self._router = router_cls.load(path)
        except RuntimeError:
            raise
        except Exception as error:
            raise RuntimeError("Routing classifier could not be loaded.") from error
        self._check_loaded_classes()

    def route_ticket(self, request: object) -> dict[str, Any]:
        """Classify one request. Raises on invalid input or a classifier failure."""
        ticket_body = _ticket_body(request)
        try:
            raw = self._router.predict(ticket_body)
        except Exception as error:
            raise RuntimeError("Routing classifier failed.") from error
        return _response(raw)

    def _check_loaded_classes(self) -> None:
        classes = getattr(getattr(self._router, "model", None), "classes_", None)
        if classes is None:
            raise RuntimeError("Routing classifier could not be loaded.")
        loaded = {str(label) for label in classes}
        if loaded != set(DEPARTMENTS) or len(list(classes)) != len(DEPARTMENTS):
            raise RuntimeError("Routing classifier departments do not match the contract.")


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


def _finite_score(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value)


def _response(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict) or set(raw) != set(RESPONSE_FIELDS):
        raise RuntimeError("Routing classifier output does not match the contract.")

    department = raw["recommended_department"]
    scores = raw["class_scores"]
    if not isinstance(department, str) or str(department) not in DEPARTMENTS:
        raise RuntimeError("Routing classifier output does not match the contract.")
    if not isinstance(scores, dict) or {str(name) for name in scores} != set(DEPARTMENTS):
        raise RuntimeError("Routing classifier output does not match the contract.")
    if len(scores) != len(DEPARTMENTS):
        raise RuntimeError("Routing classifier output does not match the contract.")
    if not all(_finite_score(score) for score in scores.values()):
        raise RuntimeError("Routing classifier output does not match the contract.")

    # The saved model labels are numpy strings. Keep the text and the scores.
    department = str(department)
    class_scores = {str(name): score for name, score in scores.items()}
    recommended_score = class_scores[department]
    if any(score > recommended_score for score in class_scores.values()):
        raise RuntimeError("Routing classifier output does not match the contract.")

    return {
        "recommended_department": department,
        "class_scores": class_scores,
    }
