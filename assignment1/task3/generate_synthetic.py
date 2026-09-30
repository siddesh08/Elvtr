#!/usr/bin/env python3
"""Generate 50 deterministic synthetic support tickets from source seed slots.

Re-run from the repository root:

    .venv/bin/python assignment1/task3/generate_synthetic.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
SOURCE_CSV = (
    REPO_ROOT
    / "assignment1"
    / "task1"
    / "dataset_samples"
    / "candidate1_aa_dataset-tickets-multi-lang-5-2-50-version.csv"
)
OUTPUT_PATH = ROOT / "outputs" / "synthetic_tickets.csv"

TAG_COLS = [f"tag_{i}" for i in range(1, 9)]

# On-label keyword filters: keep source rows whose text matches the queue.
SEED_FILTERS = {
    "Human Resources": r"payroll|benefit|employee|onboarding|\bhr\b|leave|vacation|training",
    "Returns and Exchanges": r"\breturn\b|\brefund\b|exchang|\bswap\b|replac",
    "General Inquiry": r"hours|policy|information|how do i|where can|guidelines",
    "Sales and Pre-Sales": r"pricing|quote|discount|purchase|pre-sale|salesforce|\bsaas\b",
    "Billing and Payments": r"invoice|billing|payment|charged|subscription",
}

QUEUE_PLAN = [
    ("Human Resources", 12),
    ("Returns and Exchanges", 12),
    ("General Inquiry", 10),
    ("Sales and Pre-Sales", 10),
    ("Billing and Payments", 6),
]

# Fixed frames; only {item} / {detail} come from harvested source tags.
TEMPLATES = {
    "Human Resources": [
        (
            "Request for help with {item}",
            "Dear Human Resources team,\n\nI need assistance with {item} for my employee record. "
            "Please confirm which form to use for {detail} and how long processing usually takes. "
            "I would like to complete this before the next pay cycle.\n\nThank you.",
        ),
        (
            "Question about {detail}",
            "Hello,\n\nI am writing about {detail} related to {item}. "
            "Could you explain the current policy and the steps I should follow? "
            "Please also tell me who in HR owns this request.\n\nRegards.",
        ),
    ],
    "Returns and Exchanges": [
        (
            "Return request for {item}",
            "Dear Support,\n\nI would like to return {item} from a recent order. "
            "The reason is {detail}. Please send a return authorization and the shipping address. "
            "I still have the original packaging.\n\nThank you.",
        ),
        (
            "Exchange needed: {item}",
            "Hello Returns team,\n\nI received {item} but it does not match what I ordered. "
            "I am requesting an exchange because of {detail}. "
            "Please confirm whether I should wait for the replacement before sending the original back.\n\nThanks.",
        ),
    ],
    "General Inquiry": [
        (
            "Question about {item} policy",
            "Dear Customer Support,\n\nI am not reporting an outage. I only need information about {item}. "
            "Specifically, I want to understand {detail} and where that is documented. "
            "A short pointer to the public policy page would be enough.\n\nThank you.",
        ),
        (
            "Where can I find {detail}?",
            "Hello,\n\nThis is a general question, not a technical incident. "
            "Could you tell me how {item} is handled and share {detail}? "
            "I need this to plan a visit and do not need a technician assigned.\n\nRegards.",
        ),
    ],
    "Sales and Pre-Sales": [
        (
            "Pricing question for {item}",
            "Dear Sales team,\n\nWe are evaluating {item} before purchase. "
            "Please send current pricing, volume discounts, and a quote that covers {detail}. "
            "We are not asking for break-fix support yet.\n\nThank you.",
        ),
        (
            "Pre-sales comparison: {item}",
            "Hello,\n\nI would like a pre-sales walkthrough of {item}, focused on {detail}. "
            "Could you also outline contract terms and the trial options available?\n\nBest regards.",
        ),
    ],
    "Billing and Payments": [
        (
            "Invoice question about {item}",
            "Dear Billing team,\n\nI have a question about charges related to {item}. "
            "The invoice appears to include {detail}, and I want to confirm the amount before I pay. "
            "Please point me to the line items and accepted payment methods.\n\nThank you.",
        ),
        (
            "Payment method update for {item}",
            "Hello Billing,\n\nI need to update how I pay for {item}. "
            "Please confirm the steps to change the payment method and whether {detail} will appear on the next invoice.\n\nRegards.",
        ),
    ],
}

FALLBACK_ITEMS = {
    "Human Resources": ["Employee", "Training", "HR"],
    "Returns and Exchanges": ["Warranty", "Shipment", "Replacement"],
    "General Inquiry": ["Policy", "Guidance", "Product"],
    "Sales and Pre-Sales": ["Salesforce", "SaaS", "CRM"],
    "Billing and Payments": ["Subscription", "Discount", "ERP"],
}

# Only keep harvested tags that can sit in an on-label template for that queue.
ITEM_ALLOW = {
    "Human Resources": {
        "Employee",
        "HR",
        "Training",
        "Access",
        "Login",
        "Account",
    },
    "Returns and Exchanges": {
        "Warranty",
        "Shipment",
        "Replacement",
        "Exchange",
        "Refund",
        "Swap",
        "Return",
        "Hardware",
        "Software",
        "Policy",
    },
    "General Inquiry": {
        "Policy",
        "Guidance",
        "Product",
        "Organization",
        "Documentation",
    },
    "Sales and Pre-Sales": {
        "Salesforce",
        "SaaS",
        "CRM",
        "Pricing",
        "Discount",
        "Customization",
        "Project Management",
    },
    "Billing and Payments": {
        "Subscription",
        "Discount",
        "ERP",
        "CRM",
        "AWS",
        "Accounting",
        "Cost",
        "Invoice",
        "Payment",
    },
}

FALLBACK_DETAILS = {
    "Human Resources": ["payroll setup", "benefits enrollment", "PTO balance"],
    "Returns and Exchanges": ["a refund", "an exchange", "a prepaid label"],
    "General Inquiry": ["business hours", "the published policy", "store location rules"],
    "Sales and Pre-Sales": ["annual pricing", "a written quote", "license tiers"],
    "Billing and Payments": ["a duplicate charge", "proration", "the billing cycle"],
}


def ticket_text(subject: str, body: str) -> str:
    return f"{subject}\n{body}".strip()


def harvest_tags(frame: pd.DataFrame, queue: str) -> list[str]:
    allow = ITEM_ALLOW[queue]
    values: list[str] = []
    seen: set[str] = set()
    for col in TAG_COLS[:4]:
        for raw in frame[col].dropna().astype(str):
            token = raw.strip()
            if token and token not in seen and token in allow:
                seen.add(token)
                values.append(token)
    return values


def on_label_slice(english: pd.DataFrame, queue: str) -> pd.DataFrame:
    pattern = SEED_FILTERS[queue]
    text = (
        english["subject"].fillna("").astype(str)
        + " "
        + english["body"].fillna("").astype(str)
    )
    mask = (english["queue"] == queue) & text.str.contains(
        pattern, case=False, regex=True
    )
    return english.loc[mask]


def pick(values: list[str], index: int) -> str:
    return values[index % len(values)]


def build_records(english: pd.DataFrame) -> list[dict]:
    source_bodies = set(english["body"].fillna("").astype(str).str.strip())
    source_tickets = set(
        ticket_text(s, b)
        for s, b in zip(
            english["subject"].fillna("").astype(str),
            english["body"].fillna("").astype(str),
        )
    )

    records: list[dict] = []
    n = 0
    for queue, count in QUEUE_PLAN:
        seeds = on_label_slice(english, queue)
        harvested = harvest_tags(seeds, queue)
        preferred = [t for t in FALLBACK_ITEMS[queue] if t in harvested]
        extras = [t for t in harvested if t not in preferred]
        items = preferred + extras or FALLBACK_ITEMS[queue]
        # Keep tag-like queue words off the {item} slot so "return Return" cannot occur.
        blocked = {
            "Return",
            "Refund",
            "Exchange",
            "Swap",
            "HR",
            "Payment",
            "Product",
        }
        items = [t for t in items if t not in blocked] or FALLBACK_ITEMS[queue]
        details = FALLBACK_DETAILS[queue]
        types = sorted(seeds["type"].dropna().astype(str).unique().tolist()) or [
            "Request"
        ]
        priorities = sorted(
            seeds["priority"].dropna().astype(str).unique().tolist()
        ) or ["medium"]
        templates = TEMPLATES[queue]

        for i in range(count):
            item = pick(items, i)
            detail = pick(details, i + 3)
            if detail.lower() == item.lower():
                detail = pick(FALLBACK_DETAILS[queue], i)
            subject_t, body_t = templates[i % len(templates)]
            subject = subject_t.format(item=item, detail=detail)
            body = body_t.format(item=item, detail=detail)
            if body.strip() in source_bodies or ticket_text(subject, body) in source_tickets:
                raise ValueError("Generated text copied a complete source ticket.")

            tag_cycle = items + details
            row = {
                "record_id": f"syn-{n:05d}",
                "provenance": "synthetic",
                "subject": subject,
                "body": body,
                "answer": (
                    f"Thank you for contacting {queue}. We will review your request "
                    f"about {item} and {detail} and reply with the next steps."
                ),
                "type": pick(types, i),
                "queue": queue,
                "priority": pick(priorities, i),
                "language": "en",
                "version": 400,
            }
            for t_i, col in enumerate(TAG_COLS):
                row[col] = pick(tag_cycle, i + t_i) if t_i < 4 else pd.NA
            records.append(row)
            n += 1

    if n != 50:
        raise ValueError(f"Expected 50 records, built {n}.")
    return records


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(SOURCE_CSV)
    english = raw[raw["language"].astype(str).str.lower() == "en"].copy()
    records = build_records(english)
    out = pd.DataFrame.from_records(records)
    if out["record_id"].nunique() != 50:
        raise ValueError("record_id values are not unique.")
    if set(out["provenance"].unique()) != {"synthetic"}:
        raise ValueError("All rows must have provenance=synthetic.")
    lengths = (out["subject"] + "\n" + out["body"]).str.len()
    if (lengths < 80).any():
        raise ValueError("A synthetic ticket is shorter than 80 characters.")
    out.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(out)} records to {OUTPUT_PATH}")
    print(out["queue"].value_counts().to_string())


if __name__ == "__main__":
    main()
