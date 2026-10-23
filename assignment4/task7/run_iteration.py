#!/usr/bin/env python3
"""Rerun the Task 5 request on the Task 6 tickets with a new prompt.

Model, schema, temperature, seed, and ticket bodies stay the same.
Only the system message changes.
Re-run from the repository root:

    .venv/bin/python assignment4/task7/run_iteration.py iteration1
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "task5"))
import summarize_ticket as task5

ROOT = Path(__file__).resolve().parent
IDS = [28907, 28399, 28381, 28921, 28736, 28763, 28563, 28571, 28642, 29206]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: run_iteration.py <iteration directory>")
    folder = ROOT / sys.argv[1]
    instructions = (folder / "prompt.txt").read_text(encoding="utf-8")
    out_dir = folder / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    for ticket_id in IDS:
        body = task5.load_body(ticket_id)
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": body},
        ]
        request_body = {
            "model": task5.MODEL,
            "messages": messages,
            "format": task5.OUTPUT_SCHEMA,
            "stream": False,
            "options": {"temperature": task5.TEMPERATURE, "seed": task5.SEED},
        }
        http_request = urllib.request.Request(
            task5.API_URL,
            data=json.dumps(request_body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(http_request, timeout=180) as response:
            raw = json.load(response)
        content = raw.get("message", {}).get("content", "")
        try:
            parsed = json.loads(content)
            schema_error = None
            try:
                task5.validate_summary(parsed)
            except ValueError as error:
                schema_error = str(error)
        except json.JSONDecodeError as error:
            parsed = None
            schema_error = f"model content is not JSON: {error}"
        path = out_dir / f"{ticket_id}.json"
        path.write_text(
            json.dumps(
                {
                    "ticket_id": ticket_id,
                    "output": parsed if parsed is not None else content,
                    "schema_error": schema_error,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(ticket_id, "schema_ok" if schema_error is None else schema_error)


if __name__ == "__main__":
    main()
