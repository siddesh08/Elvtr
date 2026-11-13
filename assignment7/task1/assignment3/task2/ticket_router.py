#!/usr/bin/env python3
"""Route a raw ticket body to a department.

fit and predict both take the body as it appears in the source CSV.
The class cleans the text, then trains or applies the TF-IDF vectorizer,
then trains or applies the logistic regression. The settings are the
Homework 2 baseline. This file does not read the split.
"""

from __future__ import annotations

import re
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Same settings as Homework 2. The solver sees rows in the order fit() is given.
RANDOM_STATE = 42

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


class TicketRouter:
    """Clean a raw ticket body, vectorize it, and route it."""

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

    @staticmethod
    def clean_body(text: object) -> str:
        """Homework 2 body cleaner. Lowercasing stays in the vectorizer."""
        if pd.isna(text):
            return ""
        out = str(text).translate(CHAR_MAP)
        out = BR_TAG.sub(" ", out)
        out = BROKEN_BR.sub(" ", out)
        out = out.replace("brbr", " ")
        out = UPPER_GLUE.sub(r"\1 \2", out)
        out = WHITESPACE.sub(" ", out).strip()
        return out

    def fit(self, bodies, departments) -> "TicketRouter":
        texts = [self.clean_body(text) for text in bodies]
        labels = list(departments)
        if len(texts) != len(labels):
            raise ValueError(f"{len(texts)} bodies and {len(labels)} labels")
        features = self.vectorizer.fit_transform(texts)
        self.model.fit(features, labels)
        return self

    def predict(self, bodies):
        """One raw body returns one dict. A list of bodies returns a list."""
        single = isinstance(bodies, str)
        texts = [bodies] if single else list(bodies)
        cleaned = [self.clean_body(text) for text in texts]
        probabilities = self.model.predict_proba(self.vectorizer.transform(cleaned))
        results = []
        for row in probabilities:
            scores = {
                department: float(probability)
                for department, probability in zip(self.model.classes_, row)
            }
            scores = dict(sorted(scores.items()))
            recommended = max(scores, key=scores.get)
            results.append(
                {
                    "recommended_department": recommended,
                    "class_scores": scores,
                }
            )
        if single:
            return results[0]
        return results

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
