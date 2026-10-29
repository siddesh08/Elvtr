#!/usr/bin/env python3
"""Query the Task 4 store with the five evaluation queries and score the list.

Labels are in labels.csv. I wrote those by reading the chunks. relevant_set.csv
is every chunk I counted as relevant, including ones that did not make the top
10, so recall has a denominator. This script does not relabel anything.

Re-run from the repository root:

    .venv/bin/python assignment5/task5/run_eval.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUERIES_PATH = ROOT.parent / "homework_materials" / "evaluation_queries.json"
RECORDS_PATH = ROOT.parent / "task3" / "records.json"
LABELS_PATH = ROOT / "labels.csv"
RELEVANT_PATH = ROOT / "relevant_set.csv"
LABELED_PATH = ROOT / "labeled_results.csv"
METRICS_PATH = ROOT / "metrics.csv"

sys.path.insert(0, str(ROOT.parent / "task4"))
from build_store import query

TOP_K = 10
CUTOFFS = (1, 5, 10)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_labels() -> dict[tuple[str, str], tuple[bool, str]]:
    labels: dict[tuple[str, str], tuple[bool, str]] = {}
    for row in read_csv(LABELS_PATH):
        key = (row["query_id"], row["chunk_id"])
        if key in labels:
            raise ValueError(f"duplicate label for {key}")
        if row["relevant"] not in ("yes", "no"):
            raise ValueError(f"{key} relevant must be yes or no")
        labels[key] = (row["relevant"] == "yes", row["reason"])
    return labels


def load_relevant() -> dict[str, set[str]]:
    known = {record["chunk_id"] for record in json.loads(RECORDS_PATH.read_text(encoding="utf-8"))}
    relevant: dict[str, set[str]] = {}
    for row in read_csv(RELEVANT_PATH):
        if row["chunk_id"] not in known:
            raise ValueError(f"relevant chunk is not in the records: {row['chunk_id']}")
        relevant.setdefault(row["query_id"], set()).add(row["chunk_id"])
    return relevant


def precision_at(flags: list[bool], k: int) -> tuple[int, int]:
    hit = sum(1 for flag in flags[:k] if flag)
    return hit, k


def recall_at(ids: list[str], relevant: set[str], k: int) -> tuple[int, int] | None:
    if not relevant:
        return None
    hit = len(relevant & set(ids[:k]))
    return hit, len(relevant)


def reciprocal_rank_at(flags: list[bool], k: int) -> tuple[int, int]:
    for index, flag in enumerate(flags[:k], start=1):
        if flag:
            return 1, index
    return 0, 1


def mean(pairs: list[tuple[int, int]]) -> float:
    return sum(num / den for num, den in pairs) / len(pairs)


def main() -> None:
    labels = load_labels()
    relevant = load_relevant()
    queries = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))
    labeled_rows: list[dict] = []
    by_query: dict[str, tuple[list[str], list[bool]]] = {}

    for item in queries:
        query_id = item["query_id"]
        results = query(item["query"], top_k=TOP_K)
        if len(results) != TOP_K:
            raise ValueError(f"{query_id} returned {len(results)} chunks")
        ids: list[str] = []
        flags: list[bool] = []
        for result in results:
            chunk_id = result["chunk_id"]
            key = (query_id, chunk_id)
            if key not in labels:
                raise ValueError(f"no label for {query_id} {chunk_id}")
            flag, reason = labels[key]
            ids.append(chunk_id)
            flags.append(flag)
            meta = result["metadata"]
            labeled_rows.append(
                {
                    "query_id": query_id,
                    "rank": result["rank"],
                    "chunk_id": chunk_id,
                    "distance": f"{result['distance']:.4f}",
                    "article_id": meta["article_id"],
                    "section": meta["section"],
                    "title": meta["title"],
                    "relevant": "yes" if flag else "no",
                    "reason": reason,
                }
            )
        by_query[query_id] = (ids, flags)
        labeled_yes = {chunk_id for chunk_id, flag in zip(ids, flags) if flag}
        gold = relevant.get(query_id, set())
        if labeled_yes != gold & set(ids):
            raise ValueError(f"{query_id} labels and relevant set disagree inside the top 10")

    metric_rows: list[dict] = []
    score_fns = (
        ("precision", lambda ids, flags, gold, k: precision_at(flags, k)),
        ("recall", lambda ids, flags, gold, k: recall_at(ids, gold, k)),
        ("reciprocal_rank", lambda ids, flags, gold, k: reciprocal_rank_at(flags, k)),
    )
    for metric, score_at in score_fns:
        for k in CUTOFFS:
            per_query: list[tuple[int, int]] = []
            for item in queries:
                query_id = item["query_id"]
                ids, flags = by_query[query_id]
                scored = score_at(ids, flags, relevant.get(query_id, set()), k)
                if scored is None:
                    metric_rows.append(
                        {
                            "metric": metric,
                            "k": k,
                            "query_id": query_id,
                            "numerator": "",
                            "denominator": "0",
                            "value": "",
                        }
                    )
                    continue
                numerator, denominator = scored
                per_query.append((numerator, denominator))
                metric_rows.append(
                    {
                        "metric": metric,
                        "k": k,
                        "query_id": query_id,
                        "numerator": numerator,
                        "denominator": denominator,
                        "value": f"{numerator / denominator:.3f}",
                    }
                )
            if per_query:
                metric_rows.append(
                    {
                        "metric": metric,
                        "k": k,
                        "query_id": "all",
                        "numerator": "",
                        "denominator": str(len(per_query)),
                        "value": f"{mean(per_query):.3f}",
                    }
                )

    write_csv(LABELED_PATH, labeled_rows)
    write_csv(METRICS_PATH, metric_rows)
    print(f"labeled: {LABELED_PATH}")
    print(f"metrics: {METRICS_PATH}")
    for row in metric_rows:
        if row["query_id"] == "all" or row["value"] == "":
            print(
                f"{row['metric']:16} k={row['k']:<2} {row['query_id']:6} {row['value'] or 'n/a':>6}"
            )


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
