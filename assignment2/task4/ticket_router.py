#!/usr/bin/env python3
"""Train a CPU logistic-regression baseline that routes a ticket body.

The vectorizer settings match Task 3. Re-run from the repository root:

    .venv/bin/pip install -r assignment2/homework_materials/requirements.txt
    .venv/bin/python assignment2/task4/ticket_router.py
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
CLEANED_CSV = REPO_ROOT / "assignment2" / "task1" / "outputs" / "cleaned_support_tickets.csv"
MANIFEST_CSV = REPO_ROOT / "assignment2" / "task2" / "outputs" / "split_manifest.csv"
MODEL_PATH = ROOT / "outputs" / "ticket_router.joblib"

# Same text settings as Task 3. Training rows are sorted by ticket_id
# before fit so the solver sees them in a fixed order.
RANDOM_STATE = 42


class TicketRouter:
    """Route one ticket body to a department."""

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
        )
        self.model = LogisticRegression(
            solver="lbfgs",
            class_weight="balanced",
            random_state=RANDOM_STATE,
            max_iter=200,
            C=1.0,
        )

    def fit(self, bodies, departments) -> "TicketRouter":
        features = self.vectorizer.fit_transform(bodies)
        self.model.fit(features, departments)
        return self

    def predict(self, body: str) -> dict:
        features = self.vectorizer.transform([body])
        probabilities = self.model.predict_proba(features)[0]
        scores = {
            department: float(probability)
            for department, probability in zip(self.model.classes_, probabilities)
        }
        scores = dict(sorted(scores.items()))
        recommended = max(scores, key=scores.get)
        return {
            "recommended_department": recommended,
            "class_scores": scores,
        }

    def save(self, path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"vectorizer": self.vectorizer, "model": self.model}, path)

    @classmethod
    def load(cls, path) -> "TicketRouter":
        payload = joblib.load(path)
        router = cls()
        router.vectorizer = payload["vectorizer"]
        router.model = payload["model"]
        return router


def training_rows() -> pd.DataFrame:
    cleaned = pd.read_csv(CLEANED_CSV, dtype=str)
    manifest = pd.read_csv(MANIFEST_CSV, dtype=str)
    joined = cleaned.merge(manifest, on="ticket_id", how="inner", validate="one_to_one")
    train = joined.loc[joined["split"] == "train"].copy()
    train["Body"] = train["Body"].fillna("")
    train = train.loc[train["Body"].str.strip().ne("")].copy()
    train["_tid"] = train["ticket_id"].astype(int)
    return train.sort_values("_tid")


def main() -> None:
    train = training_rows()
    router = TicketRouter()
    router.fit(train["Body"], train["Department"])

    features = router.vectorizer.transform(train["Body"])
    predicted = router.model.predict(features)
    correct = int((predicted == train["Department"].to_numpy()).sum())
    total = len(train)
    percent = 100.0 * correct / total

    second = TicketRouter()
    second.fit(train["Body"], train["Department"])
    second_predicted = second.model.predict(second.vectorizer.transform(train["Body"]))
    if list(predicted) != list(second_predicted):
        raise SystemExit("a second fit did not reproduce the training predictions")

    sample = router.predict(train["Body"].iloc[0])
    again = router.predict(train["Body"].iloc[0])
    if sample != again:
        raise SystemExit("two predictions of the same body disagreed")
    if set(sample) != {"recommended_department", "class_scores"}:
        raise SystemExit(f"unexpected predict keys: {sorted(sample)}")
    if abs(sum(sample["class_scores"].values()) - 1.0) > 1e-6:
        raise SystemExit("class scores do not sum to 1")

    router.save(MODEL_PATH)
    loaded = TicketRouter.load(MODEL_PATH)
    if loaded.predict(train["Body"].iloc[0]) != sample:
        raise SystemExit("loaded model prediction did not match")

    print(f"training records: {total}")
    print(f"predicted correctly: {correct}")
    print(f"training accuracy: {percent:.2f}%")
    print(f"vocabulary: {len(router.vectorizer.vocabulary_)}")
    print(f"iterations: {int(router.model.n_iter_.max())}")
    print(f"wrote {MODEL_PATH}")


if __name__ == "__main__":
    main()
