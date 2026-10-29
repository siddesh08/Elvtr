#!/usr/bin/env python3
"""Prepare Homework 5 vector-store records from the knowledge-base articles.

One chunk per section. This script does not embed text and does not open
LanceDB. Task 4 builds the store from the JSON written here.

Re-run from the repository root:

    .venv/bin/python assignment5/task3/prepare_records.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KNOWLEDGE_BASE = ROOT.parent / "homework_materials" / "knowledge_base"
OUTPUT_PATH = ROOT / "records.json"

# A section is a line that starts with "## ". The articles do not use deeper headings.
HEADING = re.compile(r"^## .+$", re.MULTILINE)
REQUIRED_META = ("article_id", "title")


def parse_article(text: str, source_name: str) -> tuple[dict[str, str], str]:
    """Split the frontmatter from the body. The body is the chunk source."""
    if not text.startswith("---\n"):
        raise ValueError(f"{source_name} does not start with frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{source_name} frontmatter does not close")

    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ": " not in line:
            raise ValueError(f"{source_name} has a frontmatter line I cannot split: {line}")
        key, value = line.split(": ", 1)
        meta[key] = value

    missing = [key for key in REQUIRED_META if not meta.get(key)]
    if missing:
        raise ValueError(f"{source_name} is missing {missing}")
    return meta, text[end + len("\n---\n") :]


def section_chunks(body: str, source_name: str) -> list[tuple[str, str]]:
    """Return (heading, exact file text) for each section, in file order."""
    matches = list(HEADING.finditer(body))
    if not matches:
        raise ValueError(f"{source_name} has no sections")
    if body[: matches[0].start()].strip():
        raise ValueError(f"{source_name} has text before the first section")

    chunks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[start:end]
        heading = match.group(0)[3:].strip()
        if not heading or not content.strip():
            raise ValueError(f"{source_name} has an empty section")
        chunks.append((heading, content))
    return chunks


def build_records(knowledge_base: Path) -> list[dict]:
    """Read articles in filename order and number sections from 0."""
    files = sorted(path for path in knowledge_base.glob("*.txt") if path.is_file())
    if not files:
        raise ValueError(f"no articles in {knowledge_base}")

    records: list[dict] = []
    article_ids: set[str] = set()
    for path in files:
        text = path.read_text(encoding="utf-8")
        meta, body = parse_article(text, path.name)
        article_id = meta["article_id"]
        if article_id in article_ids:
            raise ValueError(f"duplicate article_id {article_id}")
        article_ids.add(article_id)

        for position, (heading, content) in enumerate(section_chunks(body, path.name)):
            # The title is not in every section. "Limits" and "What the customer
            # provides" repeat across articles, so the passage the model embeds
            # carries the title. content stays the section text from the file.
            records.append(
                {
                    "chunk_id": f"{article_id}-{position:02d}",
                    "embedding_text": f"{meta['title']}\n\n{content}",
                    "content": content,
                    "metadata": {
                        "article_id": article_id,
                        "title": meta["title"],
                        "chunk_position": position,
                        "section": heading,
                    },
                }
            )

    chunk_ids = [record["chunk_id"] for record in records]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("chunk ids are not unique")
    return records


def main() -> None:
    records = build_records(KNOWLEDGE_BASE)
    OUTPUT_PATH.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lengths = [len(record["content"]) for record in records]
    print(f"articles: {len({record['metadata']['article_id'] for record in records})}")
    print(f"chunks: {len(records)}")
    print(f"shortest chunk: {min(lengths)} characters")
    print(f"longest chunk: {max(lengths)} characters")
    print(f"wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
