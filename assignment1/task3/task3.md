# Task 3 — Create and Inspect Synthetic Data

**Source file:** Customer Support Tickets (Tobi-Bueck / Softoft), English rows in `assignment1/task1/dataset_samples/candidate1_aa_dataset-tickets-multi-lang-5-2-50-version.csv`.

---

## 3.1 Augmentation plan

### The gap

Task 2 found two related problems in the English routing data:

1. **Label noise on some queues.** In the 20-record inspection, `queue` often disagreed with the ticket text. Human Resources and Returns and Exchanges were the worst (SaaS outages and brand-marketing questions labeled as those teams). Billing, General Inquiry, and Sales also had mismatches.
2. **Class imbalance.** Technical Support is about 29% of English tickets; General Inquiry is about 1.4% and Human Resources about 2.1%. A router trained on the source file will see far more Technical Support than the small queues, and many of those small-queue rows are not trustworthy seeds.

Naive oversampling of existing Human Resources or Returns rows would copy the same mistakes. Synthetic rows inherit seed errors, so only on-label seeds are used.

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
- **Why not simulation:** The generator does not model arrivals, channels, or SLAs over time. The goal is 50 on-label English examples for specific queues.

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

---

## 3.3 Inspect generated records

Ten records: five from a stated random draw, five chosen because they look suspicious, repetitive, or extreme. The two sets do not overlap.

### Five random

**Method:** `random.Random(20260929).sample` over `syn-00000` … `syn-00049`, then sorted. The seed is fixed so the draw can be repeated.

| record_id | Acceptable? | Issue |
| --- | --- | --- |
| `syn-00018` | No | Near-duplicate of `syn-00012`. Body says “return Warranty”; the item is a process word, not a product. |
| `syn-00024` | No | Subject is “Question about Guidance policy.” `Guidance` is a leftover source tag, not a policy topic. |
| `syn-00033` | Partial | Asks for business hours (fits General Inquiry) but also “how Guidance is handled,” which is leftover slot mixing. `type` is Incident for a how-to question. |
| `syn-00042` | Yes | Pre-purchase SaaS pricing question. Queue (Sales and Pre-Sales) matches. Minor: template still names “volume discounts” in every sales pricing frame. |
| `syn-00047` | No | “Update how I pay for Invoice” treats Invoice as a product. Billing intent is visible, but the slot is the wrong part of speech. |

### Five suspicious, repetitive, or extreme

**Method:** targeted scan for ungrammatical slot fills, duplicated frames, and `type` values that fight the template (not a second random draw).

| record_id | Acceptable? | Issue |
| --- | --- | --- |
| `syn-00000` | No | “Assistance with Employee for my employee record.” Harvested tag `Employee` is stuffed into a slot that needs a process (benefits, PTO). `type` is Change. |
| `syn-00013` | No | “I received Shipment” and “requesting an exchange because of an exchange.” Item and reason are both logistics words; the sentence is circular. |
| `syn-00017` | No | Extreme nonsense: “I received Policy but it does not match what I ordered.” Policy is not a deliverable. |
| `syn-00037` | No | “Walkthrough of Pricing, focused on annual pricing.” The product slot was filled with the word Pricing. |
| `syn-00040` | No | “Evaluating Discount before purchase.” Discount is a commercial term, not a SKU. Same sales template as several other rows. |

`syn-00042` is the only fully acceptable row in this ten. Queue alignment is often right at a coarse level (HR-ish, returns-ish, sales-ish), but slot grammar is weak, templates repeat every two rows, and `type` / `priority` rotate independently of the text.

### Changes to make to the generator

1. Give each slot a role (product vs reason vs HR process) and only fill `{item}` with product-like nouns (Salesforce, AWS, headset), never with Return, Policy, Discount, Employee, Invoice.
2. Pair templates with a fixed `type` (Request for how-to, Incident only for outages) instead of cycling Change / Incident / Problem / Request.
3. Add more than two frames per queue, and block identical (template, item, detail) triples so `syn-00012` / `syn-00018` cannot repeat.
4. Insert articles and number (“return the warranty-covered keyboard”) instead of raw tags (“return Warranty”).
5. Keep fallback detail phrases (“PTO balance”, “a prepaid label”) out of the tag columns, or store them in a dedicated `detail` field rather than `tag_4`.
6. Tighten on-label seed tags further: drop abstract source tags such as Guidance, Organization, and Documentation from General Inquiry item lists.
