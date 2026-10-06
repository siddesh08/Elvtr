#!/usr/bin/env python3
"""Assign each cleaned ticket to train, validation, or test.

No library splitter. Groups that share a cleaned Body stay together, and
the assignment inside each department targets 80/10/10. Re-run from the
repository root:

    .venv/bin/pip install -r assignment2/homework_materials/requirements.txt
    .venv/bin/python assignment2/task2/split_tickets.py
    .venv/bin/python assignment2/task2/verify_split.py
"""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
CLEANED_CSV = REPO_ROOT / "assignment2" / "task1" / "outputs" / "cleaned_support_tickets.csv"
OUTPUT_DIR = ROOT / "outputs"
MANIFEST_CSV = OUTPUT_DIR / "split_manifest.csv"

# Saved seed. The manifest should not move while later tasks are in progress.
SEED = 42
SPLITS = ("train", "validation", "test")
SHARES = {"train": 0.80, "validation": 0.10, "test": 0.10}


def build_groups(frame: pd.DataFrame) -> list[dict]:
    """One group per exact cleaned Body. The anchor row is the lowest ticket_id."""
    work = frame.copy()
    work["Body"] = work["Body"].fillna("")
    work["_tid"] = work["ticket_id"].astype(int)
    groups = []
    for _, sub in work.groupby("Body", sort=False):
        sub = sub.sort_values("_tid")
        groups.append(
            {
                "anchor": int(sub["_tid"].iloc[0]),
                "stratum": sub["Department"].iloc[0],
                "ticket_ids": sub["ticket_id"].tolist(),
                "n": len(sub),
                "departments": sorted(sub["Department"].unique()),
            }
        )
    return groups


def assign_groups(groups: list[dict]) -> dict[str, str]:
    """Give each group to the split furthest below its department target."""
    assigned: dict[str, str] = {}
    strata = sorted({group["stratum"] for group in groups})
    for stratum in strata:
        bucket = [group for group in groups if group["stratum"] == stratum]
        bucket.sort(key=lambda group: group["anchor"])
        random.Random(SEED).shuffle(bucket)
        total = sum(group["n"] for group in bucket)
        targets = {name: total * SHARES[name] for name in SPLITS}
        counts = {name: 0 for name in SPLITS}
        for group in bucket:
            choice = max(
                SPLITS,
                key=lambda name: (targets[name] - counts[name], -SPLITS.index(name)),
            )
            counts[choice] += group["n"]
            for ticket_id in group["ticket_ids"]:
                assigned[ticket_id] = choice
    return assigned


def assign_splits(frame: pd.DataFrame) -> pd.DataFrame:
    groups = build_groups(frame)
    assigned = assign_groups(groups)
    if len(assigned) != len(frame):
        raise SystemExit(f"assigned {len(assigned)} tickets, expected {len(frame)}")
    manifest = frame[["ticket_id"]].copy()
    manifest["_tid"] = manifest["ticket_id"].astype(int)
    manifest["split"] = manifest["ticket_id"].map(assigned)
    if manifest["split"].isna().any():
        raise SystemExit("a ticket was left unassigned")
    manifest = manifest.sort_values("_tid")
    return manifest[["ticket_id", "split"]]


def main() -> None:
    cleaned = pd.read_csv(CLEANED_CSV, dtype=str)
    manifest = assign_splits(cleaned)
    again = assign_splits(cleaned)
    if not manifest.equals(again):
        raise SystemExit("assignment changed on the second run")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(MANIFEST_CSV, index=False)

    # Import after the file exists so verification reads what was just written.
    from verify_split import verify

    verify(cleaned, manifest)
    counts = manifest["split"].value_counts()
    print(f"rows: {len(manifest)}")
    for name in SPLITS:
        print(f"{name}: {int(counts[name])} ({counts[name] / len(manifest):.4f})")
    print(f"wrote {MANIFEST_CSV}")


if __name__ == "__main__":
    main()
