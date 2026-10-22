#!/usr/bin/env python3
"""Fit the Homework 4 router on the canonical training split and predict validation.

Same procedure as Homework 3. The manifest decides the split. Ticket text and
labels come from the source CSV. Test rows are not read. The router in this
folder is the Homework 3 model with C=0.1.
Re-run from the repository root:

    .venv/bin/pip install -r "assignment3/homework_materials/SIDDESH NATESAN - requirements.txt"
    .venv/bin/python assignment4/task2/apply_split.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ticket_router import TicketRouter

ROOT = Path(__file__).resolve().parent
# Canonical Homework 3 files. This script does not copy or rewrite them.
MATERIALS = ROOT.parent.parent / "assignment3" / "homework_materials"
SOURCE_CSV = MATERIALS / "SIDDESH NATESAN - support_tickets - SIDDESH NATESAN - support_tickets.csv"
MANIFEST_CSV = MATERIALS / "SIDDESH NATESAN - split_manifest.csv"
MODEL_PATH = ROOT / "outputs" / "ticket_router.joblib"
PREDICTIONS_CSV = ROOT / "outputs" / "validation_predictions.csv"

PREDICTION_COLUMNS = [
    "ticket_id",
    "true_label",
    "recommended_department",
    "class_scores",
]


def load_train_and_validation() -> tuple[pd.DataFrame, pd.DataFrame]:
    source = pd.read_csv(
        SOURCE_CSV,
        dtype=str,
        usecols=["ticket_id", "Body", "Department"],
    )
    manifest = pd.read_csv(MANIFEST_CSV, dtype=str)
    if list(manifest.columns) != ["ticket_id", "split"]:
        raise SystemExit(f"unexpected manifest columns: {list(manifest.columns)}")
    if manifest["ticket_id"].duplicated().any():
        raise SystemExit("duplicate ticket_id in the manifest")
    if source["ticket_id"].duplicated().any():
        raise SystemExit("duplicate ticket_id in the source")

    unknown = sorted(set(manifest["split"]) - {"train", "validation", "test"})
    if unknown:
        raise SystemExit(f"unexpected split labels: {unknown}")

    # Test stays in the manifest file and out of this frame.
    kept = manifest.loc[manifest["split"].isin(["train", "validation"])].copy()
    merged = kept.merge(
        source,
        on="ticket_id",
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    missing = merged.loc[merged["_merge"] != "both", "ticket_id"].tolist()
    if missing:
        raise SystemExit(f"{len(missing)} manifest ids are not in the source")
    if merged["Department"].isna().any():
        raise SystemExit("a canonical ticket has no department")

    merged["_tid"] = merged["ticket_id"].astype(int)
    merged = merged.sort_values("_tid")
    train = merged.loc[merged["split"] == "train"].copy()
    validation = merged.loc[merged["split"] == "validation"].copy()
    if len(train) + len(validation) != len(kept):
        raise SystemExit("train and validation do not cover the kept manifest")
    return train, validation


def prediction_frame(validation: pd.DataFrame, predictions: list[dict]) -> pd.DataFrame:
    if len(predictions) != len(validation):
        raise SystemExit("prediction count does not match the validation split")
    rows = []
    for ticket_id, department, prediction in zip(
        validation["ticket_id"],
        validation["Department"],
        predictions,
    ):
        scores = prediction["class_scores"]
        if abs(sum(scores.values()) - 1.0) > 1e-6:
            raise SystemExit(f"scores for ticket {ticket_id} do not sum to 1")
        if max(scores, key=scores.get) != prediction["recommended_department"]:
            raise SystemExit(f"recommendation is not the top score for ticket {ticket_id}")
        rows.append(
            {
                "ticket_id": ticket_id,
                "true_label": department,
                "recommended_department": prediction["recommended_department"],
                "class_scores": json.dumps(scores, sort_keys=True),
            }
        )
    frame = pd.DataFrame(rows, columns=PREDICTION_COLUMNS)
    if frame["ticket_id"].duplicated().any():
        raise SystemExit("duplicate ticket_id in predictions")
    return frame


def recommendations(router: TicketRouter, bodies) -> list[str]:
    predicted = router.predict(list(bodies))
    return [row["recommended_department"] for row in predicted]


def main() -> None:
    train, validation = load_train_and_validation()

    router = TicketRouter()
    router.fit(train["Body"], train["Department"])
    train_predicted = recommendations(router, train["Body"])
    validation_predicted = router.predict(list(validation["Body"]))

    second = TicketRouter()
    second.fit(train["Body"], train["Department"])
    if recommendations(second, train["Body"]) != train_predicted:
        raise SystemExit("a second fit did not reproduce the training routes")
    second_validation = recommendations(second, validation["Body"])
    first_validation = [row["recommended_department"] for row in validation_predicted]
    if second_validation != first_validation:
        raise SystemExit("a second fit did not reproduce the validation routes")

    sample = router.predict(validation["Body"].iloc[0])
    if sample != router.predict(validation["Body"].iloc[0]):
        raise SystemExit("two predictions of the same body disagreed")
    if set(sample) != {"recommended_department", "class_scores"}:
        raise SystemExit(f"unexpected predict keys: {sorted(sample)}")

    frame = prediction_frame(validation, validation_predicted)
    PREDICTIONS_CSV.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(PREDICTIONS_CSV, index=False)

    reread = pd.read_csv(PREDICTIONS_CSV, dtype=str)
    if list(reread.columns) != PREDICTION_COLUMNS:
        raise SystemExit(f"prediction columns changed on write: {list(reread.columns)}")
    if not reread["ticket_id"].equals(frame["ticket_id"]):
        raise SystemExit("ticket_id changed on write")
    if not reread["true_label"].equals(frame["true_label"]):
        raise SystemExit("true_label changed on write")
    if not reread["class_scores"].equals(frame["class_scores"]):
        raise SystemExit("class_scores changed on write")

    router.save(MODEL_PATH)
    loaded = TicketRouter.load(MODEL_PATH)
    if recommendations(loaded, validation["Body"]) != first_validation:
        raise SystemExit("loaded model routes did not match")

    cleaned_train = [router.clean_body(text) for text in train["Body"]]
    changed = sum(cleaned != raw for cleaned, raw in zip(cleaned_train, train["Body"].fillna("")))
    empty = sum(text == "" for text in cleaned_train)

    print(f"training records: {len(train)}")
    print(f"validation records: {len(validation)}")
    print(f"training bodies changed by cleaning: {changed}")
    print(f"training bodies empty after cleaning: {empty}")
    print(f"vocabulary: {len(router.vectorizer.vocabulary_)}")
    print(f"iterations: {int(router.model.n_iter_.max())}")
    print(f"classes: {list(router.model.classes_)}")
    print(f"wrote {MODEL_PATH}")
    print(f"wrote {PREDICTIONS_CSV}")


if __name__ == "__main__":
    main()
