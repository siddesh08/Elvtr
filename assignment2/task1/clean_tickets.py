#!/usr/bin/env python3
"""Clean support-ticket text for the week 2 routing task.

The source CSV is left unchanged. Cleaning is plain string and regex
work (no text-cleaning package). Dependencies are the Week 2 pin file.
Re-run from the repository root:

    .venv/bin/pip install -r assignment2/homework_materials/requirements.txt
    .venv/bin/python assignment2/task1/clean_tickets.py
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
SOURCE_CSV = (
    REPO_ROOT
    / "assignment2"
    / "homework_materials"
    / "SIDDESH NATESAN - support_tickets - SIDDESH NATESAN - support_tickets.csv"
)
OUTPUT_DIR = ROOT / "outputs"
CLEANED_CSV = OUTPUT_DIR / "cleaned_support_tickets.csv"

# <br>, <br/>, and <br />. Placeholder tags such as <tel_num> are not this pattern.
BR_TAG = re.compile(r"<br\s*/?>", re.IGNORECASE)
# One ticket dropped the ">" so the tag reads "<brWarm" instead of "<br>Warm".
BROKEN_BR = re.compile(r"<br(?=[A-Za-z])", re.IGNORECASE)
# Sentence punctuation glued to the next word: "Team,I" / "persists.Could".
# Lowercase stays put so "Node.js" and ".com" are not split.
UPPER_GLUE = re.compile(r"([,.:;!?])([A-Z])")
WHITESPACE = re.compile(r"\s+")

CHAR_MAP = str.maketrans(
    {
        "\u2018": "'",  # ‘
        "\u2019": "'",  # ’
        "\u201c": '"',  # “
        "\u201d": '"',  # ”
        "\u00a0": " ",  # nbsp
    }
)


def clean_body(text: object) -> str:
    if pd.isna(text):
        return ""
    out = str(text).translate(CHAR_MAP)
    out = BR_TAG.sub(" ", out)
    out = BROKEN_BR.sub(" ", out)
    out = out.replace("brbr", " ")
    out = UPPER_GLUE.sub(r"\1 \2", out)
    out = WHITESPACE.sub(" ", out).strip()
    return out


def main() -> None:
    source = pd.read_csv(SOURCE_CSV, dtype=str)
    cleaned = source.copy()
    cleaned["Body"] = source["Body"].map(clean_body)

    if len(cleaned) != len(source):
        raise SystemExit(f"row count changed: {len(source)} -> {len(cleaned)}")
    if not cleaned["ticket_id"].equals(source["ticket_id"]):
        raise SystemExit("ticket_id values changed")
    if cleaned["ticket_id"].duplicated().any():
        raise SystemExit("duplicate ticket_id in cleaned file")
    for column in ("Department", "Priority", "Tags"):
        if not cleaned[column].equals(source[column]):
            raise SystemExit(f"{column} changed")

    # A second pass must be a no-op, otherwise the cleaner is not stable.
    again = cleaned["Body"].map(clean_body)
    if not again.equals(cleaned["Body"]):
        raise SystemExit("cleaning is not idempotent")

    raw = source["Body"]
    filled = raw.fillna("")
    if filled.str.contains(r"\.js", regex=True).sum() != cleaned["Body"].str.contains(r"\.js", regex=True).sum():
        raise SystemExit(".js sequences were split")
    if cleaned["Body"].str.contains(r"<br", case=False, regex=True).any():
        raise SystemExit("a <br> tag survived cleaning")
    if not (cleaned.loc[source["ticket_id"] == "33", "Body"].str.contains("Türklingel")).all():
        raise SystemExit("umlaut in ticket 33 was altered")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(CLEANED_CSV, index=False)

    reread = pd.read_csv(CLEANED_CSV, dtype=str).fillna("")
    if not reread["ticket_id"].equals(cleaned["ticket_id"]):
        raise SystemExit("ticket_id changed on write")
    if not reread["Body"].equals(cleaned["Body"]):
        raise SystemExit("Body changed on write")

    changed = cleaned["Body"] != filled
    print(f"rows: {len(cleaned)}")
    print(f"bodies changed: {int(changed.sum())}")
    print(f"wrote {CLEANED_CSV}")


if __name__ == "__main__":
    main()
