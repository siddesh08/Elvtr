#!/usr/bin/env python3
"""Build train, validation, and test feature vectors from the cleaned tickets.

Inputs are the cleaned CSV and the Task 2 manifest. The vectorizer is fit
on training bodies only. Re-run from the repository root:

    .venv/bin/pip install -r assignment2/homework_materials/requirements.txt
    .venv/bin/python assignment2/task3/preprocess.py
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
CLEANED_CSV = REPO_ROOT / "assignment2" / "task1" / "outputs" / "cleaned_support_tickets.csv"
MANIFEST_CSV = REPO_ROOT / "assignment2" / "task2" / "outputs" / "split_manifest.csv"
OUTPUT_DIR = ROOT / "outputs"

SPLITS = ("train", "validation", "test")

# Fit on the training split only. min_df drops a token that appears in one
# ticket. max_df drops a token that appears in almost every ticket.
VECTORIZER = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
)


def load_joined() -> pd.DataFrame:
    cleaned = pd.read_csv(CLEANED_CSV, dtype=str)
    manifest = pd.read_csv(MANIFEST_CSV, dtype=str)
    joined = cleaned.merge(manifest, on="ticket_id", how="inner", validate="one_to_one")
    if len(joined) != len(cleaned):
        raise SystemExit(f"join dropped rows: {len(cleaned)} -> {len(joined)}")
    unknown = sorted(set(joined["split"]) - set(SPLITS))
    if unknown:
        raise SystemExit(f"unexpected split labels: {unknown}")
    joined["Body"] = joined["Body"].fillna("")
    joined["_tid"] = joined["ticket_id"].astype(int)
    return joined.sort_values("_tid")


def balanced_class_weights(labels: pd.Series) -> pd.DataFrame:
    """Inverse-frequency weights. Same rule as scikit-learn's "balanced"."""
    counts = labels.value_counts()
    n_rows = int(counts.sum())
    n_classes = int(counts.shape[0])
    rows = []
    for department, count in counts.sort_index().items():
        rows.append(
            {
                "Department": department,
                "train_rows": int(count),
                "weight": n_rows / (n_classes * int(count)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    joined = load_joined()
    empty = joined["Body"].str.strip().eq("")
    if list(joined.loc[empty, "ticket_id"]) != ["28902"]:
        raise SystemExit(f"unexpected empty bodies: {joined.loc[empty, 'ticket_id'].tolist()}")
    usable = joined.loc[~empty].copy()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pieces = {}
    for split in SPLITS:
        piece = usable.loc[usable["split"] == split, ["ticket_id", "Department", "Body"]]
        pieces[split] = piece
        piece[["ticket_id", "Department"]].to_csv(OUTPUT_DIR / f"{split}_index.csv", index=False)

    vectorizer = VECTORIZER
    train_matrix = vectorizer.fit_transform(pieces["train"]["Body"])
    matrices = {"train": train_matrix}
    for split in ("validation", "test"):
        matrices[split] = vectorizer.transform(pieces[split]["Body"])

    n_features = train_matrix.shape[1]
    for split, matrix in matrices.items():
        if matrix.shape[1] != n_features:
            raise SystemExit(f"{split} has {matrix.shape[1]} features, train has {n_features}")
        if matrix.shape[0] != len(pieces[split]):
            raise SystemExit(f"{split} row count does not match its index")
        sparse.save_npz(OUTPUT_DIR / f"{split}_vectors.npz", matrix)

    weights = balanced_class_weights(pieces["train"]["Department"])
    weights.to_csv(OUTPUT_DIR / "class_weights.csv", index=False)
    joblib.dump(vectorizer, OUTPUT_DIR / "vectorizer.joblib")

    analyzer = vectorizer.build_analyzer()
    print("analyzer Smart-Türklingel:", analyzer("Smart-Türklingel"))
    print("analyzer <tel_num>:", analyzer("Our contact number is <tel_num>."))
    print(f"vocabulary: {n_features}")
    for split, matrix in matrices.items():
        print(f"{split}: rows={matrix.shape[0]} nnz={matrix.nnz}")
    print(weights.to_string(index=False))
    print(f"wrote {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
