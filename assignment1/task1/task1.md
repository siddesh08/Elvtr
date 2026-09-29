# Task 1 — Find and Select a Dataset

**Intended use/ Goal of Dataset:** given the text of a newly arrived support ticket, route it to the appropriate support team.

## Three candidate datasets

1. **Customer Support Tickets** (Tobi-Bueck / Softoft)
2. **IT Service Ticket Classification Dataset** (Kaggle / Adison Goh)
3. **Bitext Customer Service Tagged Training Dataset**

---

## 1.1 Candidate records

### Candidate 1 — Customer Support Tickets

- **Name and source URL:** Customer Support Tickets (Tobi-Bueck / Softoft). Dataset card: https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets. DOI: `10.57967/hf/6184`.
- **Version or retrieval date:** Hugging Face revision `ddf1c81a5475992c4fa6752bf1e8b4e31f07bbeb` (last modified 2026-06-28). Retrieved 2026-09-28.
- **Stated usage terms:** CC BY-NC 4.0. Public download with no approval gate. Educational analysis is allowed. Commercial use is prohibited. Attribution is required.
- **Required fields:** Ticket text: `subject` and `body`. Routing label: `queue` (department / support team).
- **Optional context fields:** `priority`, `type` (Incident / Request / Problem / Change), `language`, `tag_1`–`tag_8`, agent `answer`. No timestamp or channel field.
- **Number of usable records:** 28,261 English records (`language=en`) out of 61,765 total in the combined Hugging Face snapshot. The remainder are German.

### Candidate 2 — IT Service Ticket Classification Dataset

- **Name and source URL:** IT Service Ticket Classification Dataset. Kaggle listing: https://www.kaggle.com/datasets/adisongoh/it-service-ticket-classification-dataset. File: `all_tickets_processed_improved_v3.csv`.
- **Version or retrieval date:** Published file `all_tickets_processed_improved_v3.csv`. Kaggle listing last updated about 2023. Retrieved 2026-09-28.
- **Stated usage terms:** CC0: Public Domain. Educational analysis is allowed. A free Kaggle account is typically required to download; no special approval is stated.
- **Required fields:** Ticket text: `Document`. Routing label: `Topic_group` (`Hardware`, `HR Support`, `Access`, `Miscellaneous`, `Storage`, `Purchase`, `Internal Project`, `Administrative rights`).
- **Optional context fields:** None in this file (text and label only). No priority, tags, timestamp, or channel.
- **Number of usable records:** 47,837 labeled tickets. Presented as English IT helpdesk text; there is no language column.

### Candidate 3 — Bitext Customer Service Tagged Training Dataset

- **Name and source URL:** Bitext - Customer Service Tagged Training Dataset for LLM-based Virtual Assistants. Dataset card: https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset. File: `Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv`.
- **Version or retrieval date:** v11 in the filename. Hugging Face listing last modified 2024-07-18 (revision `430d1a89bd93bd1fa23c16f29dd53e73f0087443`). Retrieved 2026-09-28.
- **Stated usage terms:** CDLA-Sharing-1.0. Public download with no approval gate. Educational analysis is allowed. Redistribution of the data must remain under CDLA-Sharing-1.0.
- **Required fields:** Ticket-text analog: `instruction` (user request). Routing-like label: `category` (10 high-level groups). Finer label: `intent` (27 classes).
- **Optional context fields:** `flags` (language-variation tags) and `response` (example agent reply). No timestamp, channel, or priority.
- **Number of usable records:** 26,872 English instruction/response pairs. The dataset is English-only.

None of the three licenses prohibit educational analysis.

---

## 1.2 Selection

### Comparison of candidates

| Dataset | Source | Version / date | Usage terms | Ticket text | Routing label | Optional context | Usable English records |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Customer Support Tickets (Tobi-Bueck / Softoft) | [Hugging Face](https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets) | Revision `ddf1c81` (2026-06-28); retrieved 2026-09-28 | CC BY-NC 4.0 | `subject` + `body` | `queue` | Priority, type, tags, language, agent answer | 28,261 of 61,765 |
| IT Service Ticket Classification Dataset | [Kaggle](https://www.kaggle.com/datasets/adisongoh/it-service-ticket-classification-dataset) | `all_tickets_processed_improved_v3.csv` (~2023); retrieved 2026-09-28 | CC0: Public Domain | `Document` | `Topic_group` | None in this file | 47,837 |
| Bitext Customer Service Tagged Training Dataset | [Hugging Face](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset) | v11 file (listing 2024-07-18); retrieved 2026-09-28 | CDLA-Sharing-1.0 | `instruction` | `category` (or `intent`) | Flags, example response | 26,872 |

### Chosen dataset

**Selected dataset:** Customer Support Tickets (Tobi-Bueck / Softoft).

Reasons for choosing this dataset:
- Each record is a support email with natural-language text available at arrival (`subject`, `body`) and a categorical routing target (`queue`) that names the support team
- It also includes useful context (priority, type, tags, language) and enough English examples across several queues for later inspection and profiling
- The other two candidates remain eligible, but the Kaggle set is a pre-cleaned text-and-label file with no arrival metadata, and Bitext is synthetic chatbot utterances rather than full tickets
