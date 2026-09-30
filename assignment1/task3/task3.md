# Task 3 — Create and Inspect Synthetic Data

**Selected source:** Customer Support Tickets (Tobi-Bueck / Softoft), English rows in `assignment1/task1/dataset_samples/candidate1_aa_dataset-tickets-multi-lang-5-2-50-version.csv`.

This file records the Task 3.1 plan and the Task 3.2 generator. The 10-record inspection (3.3) will be added after those records are reviewed.

---

## 3.1 Augmentation plan

### The gap

Task 2 found two related problems in the English routing data:

1. **Label noise on some queues.** In the 20-record inspection, `queue` often disagreed with the ticket text. Human Resources and Returns and Exchanges were the worst (SaaS outages and brand-marketing questions labeled as those teams). Billing, General Inquiry, and Sales also had mismatches.
2. **Class imbalance.** Technical Support is about 29% of English tickets; General Inquiry is about 1.4% and Human Resources about 2.1%. A router trained on the source file will see far more Technical Support than the small queues, and many of those small-queue rows are not trustworthy seeds.

Naive oversampling of existing Human Resources or Returns rows would copy the same mistakes. The assignment notes that synthetic records inherit seed errors, so seeds must be on-label.

The gap synthetic data can reasonably address: **too few English tickets whose text clearly belongs to the small, noisy queues.**

### The population or slice to add

Add exactly 50 **English** synthetic tickets aimed at the underrepresented and poorly labeled queues, with text that matches the label:

| Queue | Planned count | Intended content |
| --- | --- | --- |
| Human Resources | 12 | Benefits, payroll, PTO, onboarding, employee records |
| Returns and Exchanges | 12 | Return, refund, wrong item, size/exchange |
| General Inquiry | 10 | Hours, store/policy questions that are not incidents |
| Sales and Pre-Sales | 10 | Pricing, quotes, product comparison before purchase |
| Billing and Payments | 6 | Invoice, charge, payment method (on-label only) |

Each synthetic row will have:

- a filled `subject` and a `body` long enough to route (not the sub-80-character stubs from Task 2)
- `queue` aligned with that content
- `language = en`
- `record_id` unique and stable (for example `syn-00000` … `syn-00049`)
- `provenance = synthetic`

Seeds will be short **slots** (product tokens, issue nouns, polite openers) taken from source rows that look on-label, not whole emails. Source tickets with unclear text or questionable `queue` will not be used as seeds.

### Generation approach and why it fits

**Technique: templates** (slot filling). This is not augmentation, combinational stitching of whole tickets, or process simulation.

- **Templates:** Fixed subject/body frames with slots such as `{issue}`, `{item}`, `{order_ref}`, `{account_action}`. Filling those frames produces new arrival text that never copies a complete source ticket, runs locally without an LLM, and is deterministic.
- **Why not augmentation:** Rewriting one existing HR/Returns ticket would stay too close to the original (risk of copying the full text) and would keep a bad label if the seed was misrouted.
- **Why not combinational (as the main method):** Crossing a full subject from ticket A with a full body from ticket B produced mixed-product, incoherent emails in Task 2. Slots may be drawn from more than one seed row; whole tickets will not be concatenated.
- **Why not simulation:** We are not modeling arrivals, channels, or SLAs over time. We only need 50 on-label English examples for specific queues.

Templates fit the gap because the frame **forces** HR-like or return-like language onto the matching `queue`, which random remixes of the source file cannot do. Fifty rows will not rebalance 16,338 English tickets, but they add a clean slice those classes currently lack.

---

## 3.2 Generated records

Re-run from the repository root:

```bash
.venv/bin/python assignment1/task3/generate_synthetic.py
```

- Code: `assignment1/task3/generate_synthetic.py`
- Output: `assignment1/task3/outputs/synthetic_tickets.csv` (exactly 50 rows)

The script loads English source rows, keeps only on-label seeds (queue plus a keyword filter), harvests short tag tokens that appear in an allowlist, and fills two rotating templates per queue. It does not copy `subject` or `body` from any source ticket. Every row has `record_id` `syn-00000` … `syn-00049` and `provenance = synthetic`. The counts match the 3.1 table (12 / 12 / 10 / 10 / 6). A re-run produces the same file.
