# Task 2 — Inspect and Profile the Dataset

**Selected dataset:** Customer Support Tickets (Tobi-Bueck / Softoft), file `assignment1/task1/dataset_samples/candidate1_aa_dataset-tickets-multi-lang-5-2-50-version.csv`.

**Environment:** `.venv` with Python 3.12.13 and `assignment1/homework_materials/requirements.txt` (`pandas==3.0.5`).

**How to re-run the profiler** (from the repository root):

```bash
.venv/bin/python assignment1/task2/profile_dataset.py
```

Outputs:

- `assignment1/task2/outputs/profile_report.md`
- `assignment1/task2/outputs/inspection_sample.csv`

**Stable IDs:** the source file has no ticket id. `record_id` is `src-{zero-padded 0-based row index}` in this CSV, assigned in `assignment1/task2/profile_dataset.py`.

---

## 2.1 Inspect source record sample

### Selection method

**Method: stratified systematic sampling (equal allocation).** This is a representative design, not a mix of representative and targeted sampling.

| Method | Used? |
| --- | --- |
| Stratified | Yes. The stratum is `queue` (the routing label). Every class appears in the sample. |
| Systematic | Yes. Inside each queue, rows are ordered by `record_id` and the 25th and 75th percentile positions are taken, not a random draw. |
| Random | No. There is no random seed. |
| Cluster | No. Related groups (for example by `version`) were not sampled as units. |
| Targeted | No. Short texts, missing subjects, and likely mislabels were not sought on purpose. |

Procedure:

1. Keep only rows with `language == en`.
2. Assign `record_id` as above.
3. Within each of the 10 `queue` values, sort by `record_id` and take the records at the 25th and 75th percentiles of that ordered list.

That yields exactly 20 English records, two per routing class.

Equal allocation (2 per queue) is representative of **class coverage**, not of **class frequency**. Technical Support is about 29% of English tickets, but it still gets the same 2 records as General Inquiry (~1%). A size-proportional sample would have put more rows in the large queues.

A common inspection mix is representative plus targeted (for example 10 stratified records plus 10 chosen because they are short, missing a subject, or look mislabeled). This sample is only the representative half. Edge cases still showed up, but that was luck of the systematic picks, not a targeted rule.

### Observations

| record_id | queue | Observation |
| --- | --- | --- |
| `src-07636` | Billing and Payments | Missing subject. Body is a technical Oracle/PHP data-sync failure, not a billing issue. Queue looks wrong. |
| `src-21177` | Billing and Payments | Subject matches billing (`Subscription Renewal Issue`), but the body is only “Faced a billing problem.” Too thin to route confidently; still the better-aligned billing example of the pair. |
| `src-07157` | Customer Service | Missing subject. IBM Cloud Kubernetes / analytics integration request. Could be Technical or Product Support rather than Customer Service. |
| `src-21312` | Customer Service | Coherent incident about data-analytics tools after an update. Customer Service is plausible; Technical Support would also fit. |
| `src-05987` | General Inquiry | Long incident affecting many unrelated products (KNIME, Slack, a soundbar, RAM). Reads as a generated mix, not a real inquiry. Low priority despite a multi-product outage. |
| `src-20151` | General Inquiry | Missing subject; lowercase body. Feature request for analytics tools. General Inquiry is a weak label; Product Support would be closer. |
| `src-06753` | Human Resources | Missing subject. SaaS outage from server overload. No HR content. Queue looks wrong. |
| `src-19957` | Human Resources | Brand-growth / marketing strategy request. No HR content. Queue looks wrong. |
| `src-06311` | IT Support | Marketing-agency “digital strategy” with vague software/hardware problems. IT Support is possible; the subject overstates urgency relative to the detail given. |
| `src-20061` | IT Support | Device/app disconnects after updates. Reasonable IT/Technical incident. The `answer` field is only a stub (“provide more details”). |
| `src-06059` | Product Support | Missing subject. Healthcare unauthorized-access report that already describes remediation. Sounds like a security incident more than product support. |
| `src-20961` | Product Support | Clear request for Oracle 19c medical-data storage practices. Product/IT support is a fair label. |
| `src-07148` | Returns and Exchanges | Digital brand / SEO / email marketing question. Nothing about a return or exchange. Queue looks wrong. |
| `src-20711` | Returns and Exchanges | Same mismatch: brand-growth advice, not returns. Short but readable. |
| `src-05762` | Sales and Pre-Sales | Missing subject. Django 3.2 SaaS integration how-to. Pre-sales is possible; Technical Support is equally plausible. |
| `src-19118` | Sales and Pre-Sales | Asks support to *draft* a medical-data security enhancement request. Odd speech act for a ticket; not really sales. |
| `src-06628` | Service Outages and Maintenance | SaaS outage with troubleshooting already tried. Queue and type (Incident) fit. |
| `src-20823` | Service Outages and Maintenance | Capacity upgrade for peak load. Fits a change/maintenance queue. |
| `src-06861` | Technical Support | Data-analytics crashes and GPU drivers. Queue fits. |
| `src-20735` | Technical Support | System outage affecting “Django SAP ERP.” Queue fits; product list looks synthetic. |

**Sample-level takeaway:** English ticket bodies are usually usable as arrival text, but subjects are often missing, some bodies are too short, and `queue` frequently disagrees with the text (especially Human Resources and Returns and Exchanges in this sample). Several tickets look templated or list unrelated products.

---

## 2.2 Profile

Reproducible code: `assignment1/task2/profile_dataset.py`.

Saved report: `assignment1/task2/outputs/profile_report.md`.

Headline results (English analysis set unless noted):

- 28,587 records, 16 source columns.
- 16,338 records after `language == en`.
- Grain: one support-email ticket per row.
- Ticket text: `subject` + `body`. Routing label: `queue`.
- `subject` is missing in 16.0% of English rows; `body` is complete; later tag columns are mostly empty.
- Largest English queue is Technical Support (29.0%); smallest is General Inquiry (1.4%).
- Combined ticket-text length: min 18, median 416, max 1,189 characters; 276 English rows (1.7%) are under 80 characters.
- 0 exact duplicate English ticket texts.
