#!/usr/bin/env python3
"""Call the local Ollama chat API.

The client stores the Ollama URL and nothing else. Every call_llm request
supplies its own prompt, model, generation settings, and optional schema.
This module does not load a model and does not summarize a ticket.
call_llm follows assignment6/task1/llm_contract.md.
"""

from __future__ import annotations

import json
import math
import os
import urllib.error
import urllib.request
from typing import Any

DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://host.docker.internal:8003")
REQUEST_TIMEOUT_SECONDS = 180


class LLMClient:
    """Send one chat request to the stored Ollama URL."""

    def __init__(self, ollama_url: str = DEFAULT_OLLAMA_URL) -> None:
        if not isinstance(ollama_url, str) or not ollama_url.strip():
            raise ValueError("ollama_url must be a non-empty string.")
        self.ollama_url = ollama_url

    def call_llm(self, request: object) -> dict[str, str]:
        """Validate one request, call Ollama, and return the message text."""
        payload = _payload(request)
        raw = self._post(payload)
        return {"content": _content(raw, stream=payload["stream"])}

    def _post(self, payload: dict[str, Any]) -> bytes:
        body = {
            "model": payload["model"],
            "messages": [{"role": "user", "content": payload["prompt"]}],
            "stream": payload["stream"],
            "options": payload["options"],
        }
        if "format" in payload:
            body["format"] = payload["format"]
        encoded = json.dumps(body).encode("utf-8")
        http_request = urllib.request.Request(
            _chat_url(self.ollama_url),
            data=encoded,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as error:
            raise RuntimeError("Ollama request failed.") from error


def _chat_url(ollama_url: str) -> str:
    base = ollama_url.strip().rstrip("/")
    if base.endswith("/api/chat"):
        return base
    return f"{base}/api/chat"


def _payload(request: object) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be a dictionary.")
    prompt = _required_text(request, "prompt")
    model = _required_text(request, "model")
    if "stream" not in request:
        raise ValueError("stream is required.")
    stream = request["stream"]
    if not isinstance(stream, bool):
        raise ValueError("stream must be a boolean.")
    if "options" not in request:
        raise ValueError("options is required.")
    options = request["options"]
    if not isinstance(options, dict):
        raise ValueError("options must be an object.")
    _check_options(options)
    payload = {
        "prompt": prompt,
        "model": model,
        "stream": stream,
        "options": dict(options),
    }
    if "format" not in request or request["format"] is None:
        return payload
    schema = request["format"]
    if not isinstance(schema, dict):
        raise ValueError("format must be an object or null.")
    payload["format"] = schema
    return payload


def _required_text(request: dict, field: str) -> str:
    if field not in request:
        raise ValueError(f"{field} is required.")
    value = request[field]
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string.")
    if not value.strip():
        raise ValueError(f"{field} must contain non-whitespace text.")
    return value


def _check_options(options: dict) -> None:
    for key, value in options.items():
        if not isinstance(key, str):
            raise ValueError("options keys must be strings.")
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            if not math.isfinite(value):
                raise ValueError("options values must be numbers, strings, or booleans.")
            continue
        if isinstance(value, str):
            continue
        raise ValueError("options values must be numbers, strings, or booleans.")


def _content(raw: bytes, stream: bool) -> str:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError("Ollama response did not contain message content.") from error
    if not stream:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as error:
            raise RuntimeError("Ollama response did not contain message content.") from error
        return _message_content(payload)

    parts: list[str] = []
    saw_done = False
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError("Ollama response did not contain message content.") from error
        if not isinstance(payload, dict):
            raise RuntimeError("Ollama response did not contain message content.")
        message = payload.get("message")
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            parts.append(message["content"])
        if payload.get("done") is True:
            saw_done = True
    content = "".join(parts)
    if not saw_done or not isinstance(content, str) or not content.strip():
        raise RuntimeError("Ollama response did not contain message content.")
    return content


def _message_content(payload: object) -> str:
    if not isinstance(payload, dict):
        raise RuntimeError("Ollama response did not contain message content.")
    message = payload.get("message")
    if not isinstance(message, dict):
        raise RuntimeError("Ollama response did not contain message content.")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Ollama response did not contain message content.")
    return content
