#!/usr/bin/env python3
"""Check the split manifest against the cleaned tickets and the split policy.

Re-run from the repository root:

    .venv/bin/python assignment2/task2/verify_split.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from split_tickets import CLEANED_CSV, MANIFEST_CSV, SEED, SHARES, SPLITS, assign_splits

# Whole groups of size at most 4, so the realized shares should stay near the targets.
SHARE_TOLERANCE = 0.01
# General Inquiry is the smallest department (419 rows). 20 is well under a 10% holdout.
MIN_PER_DEPARTMENT = 20


def verify(cleaned: pd.DataFrame, manifest: pd.DataFrame) -> None:
    expected_columns = ["ticket_id", "split"]
    if list(manifest.columns) != expected_columns:
        raise SystemExit(f"manifest columns are {list(manifest.columns)}")
    if manifest["ticket_id"].duplicated().any():
        raise SystemExit("duplicate ticket_id in the manifest")
    if set(manifest["ticket_id"]) != set(cleaned["ticket_id"]):
        raise SystemExit("manifest ticket ids do not match the cleaned file")
    unknown = sorted(set(manifest["split"]) - set(SPLITS))
    if unknown:
        raise SystemExit(f"unexpected split labels: {unknown}")
    if manifest["split"].isna().any():
        raise SystemExit("blank split label")

    recomputed = assign_splits(cleaned)
    left = manifest.sort_values("ticket_id").reset_index(drop=True)
    right = recomputed.sort_values("ticket_id").reset_index(drop=True)
    if not left.equals(right):
        raise SystemExit(f"manifest does not match seed {SEED}")

    shares = manifest["split"].value_counts(normalize=True)
    for name in SPLITS:
        gap = abs(float(shares[name]) - SHARES[name])
        if gap > SHARE_TOLERANCE:
            raise SystemExit(f"{name} share is {shares[name]:.4f}, target {SHARES[name]:.2f}")

    body = cleaned[["ticket_id", "Body", "Department"]].copy()
    body["Body"] = body["Body"].fillna("")
    merged = body.merge(manifest, on="ticket_id", how="left")
    split_per_body = merged.groupby("Body", sort=False)["split"].nunique()
    if (split_per_body > 1).any():
        raise SystemExit("a repeated Body was placed in more than one split")

    coverage = pd.crosstab(merged["Department"], merged["split"])
    missing = [name for name in SPLITS if name not in coverage.columns]
    if missing:
        raise SystemExit(f"missing split column in coverage table: {missing}")
    short = coverage[list(SPLITS)] < MIN_PER_DEPARTMENT
    if short.any().any():
        raise SystemExit(f"a department has fewer than {MIN_PER_DEPARTMENT} rows in a split")


def main() -> None:
    if not MANIFEST_CSV.exists():
        raise SystemExit(f"missing {MANIFEST_CSV}; run split_tickets.py first")
    cleaned = pd.read_csv(CLEANED_CSV, dtype=str)
    manifest = pd.read_csv(MANIFEST_CSV, dtype=str)
    verify(cleaned, manifest)
    print(f"ok {MANIFEST_CSV}")


if __name__ == "__main__":
    main()
