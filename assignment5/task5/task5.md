# Task 5 — Evaluate Retrieval

I sent the five queries in `evaluation_queries.json` through the Task 4 store, unchanged, and took the top 10 for each. The query code is `run_eval.py`. The labels are `labeled_results.csv`. The metrics are `metrics.csv`.

Re-run from the repository root:

```bash
.venv/bin/python assignment5/task5/run_eval.py
```

The script does not decide relevance. It joins the live ranking to `labels.csv`. If a returned chunk has no label, it stops.

## What I counted as relevant

A chunk is relevant when it contains a fact I would use in the answer, or the split between the two procedures the query asks for. A shared product name is not enough. The 2023 maintenance notice is not a current incident. The audio article is not the flicker procedure. Firmware is not an address change.

`relevant_set.csv` is the full set, including chunks that did not come back in the top 10. Recall is against that set. The top 10 labels and that file agree on every chunk that did come back. Q005 is empty. I searched the knowledge base for an authenticator, a security key, and multifactor. The only hit is the password-reset article, which says the customer may have to update multifactor settings at the next sign-in. That is not enrolling a key or revoking one.

Chunks I counted that the top 10 missed:

- Q001. `KB-AWS-NEG-003-03`. The health article says it is not the scheduled-maintenance notice.
- Q002. `KB-JIRA-NEG-001-00` and `KB-JIRA-NEG-001-03`. The notification article does not design statuses or transitions.
- Q003. `KB-SHIP-001-00`, `KB-SHIP-001-01`, `KB-SHIP-001-02`. `KB-SHIP-001-01` is the chunk that says expedited delivery is two to three business days.
- Q004. The store-return overview, the 21-day policy, and the return intake (`KB-SAM-NEG-002-00` through `02`). The technician overview, the dispatch section, and the line that says retail returns are handled separately (`KB-SAM-TV-002-00`, `02`, `03`).

## Metrics

Three metrics, at k = 1, 5, and 10. k = 1 is the first chunk. k = 5 is the default on `VectorStore.query`. k = 10 is the list I labeled.

**Precision@k.** Relevant chunks in the top k, divided by k. Task 6 will put retrieved chunks next to the ticket. A slot filled by the maintenance notice or the audio article is a wrong fact in that prompt. Precision is the fraction of the list I can use.

**Recall@k.** Relevant chunks in the top k, divided by the number I marked for that query. Q002, Q003, and Q004 each ask for two procedures. Precision can look fine while the second procedure never shows up. Q005 has no relevant chunk, so recall is not defined there. The "all" row is the unweighted mean of Q001 through Q004.

**Reciprocal rank@k.** 1 divided by the rank of the first relevant chunk, or 0 if none of the top k is relevant. This is how far down the list I have to read before there is anything I can use. Q001 is the query where that is not rank 1.

The "all" row for precision and reciprocal rank is the unweighted mean of all five queries. Q005 is a real zero in those two. It is left out of the recall mean.

### Precision

| query | k=1 | k=5 | k=10 |
| --- | ---: | ---: | ---: |
| Q001 | 0.000 | 0.400 | 0.300 |
| Q002 | 1.000 | 0.800 | 0.600 |
| Q003 | 1.000 | 0.600 | 0.400 |
| Q004 | 1.000 | 0.800 | 0.500 |
| Q005 | 0.000 | 0.000 | 0.000 |
| all | 0.600 | 0.520 | 0.360 |

### Recall

| query | k=1 | k=5 | k=10 |
| --- | ---: | ---: | ---: |
| Q001 | 0.000 | 0.500 | 0.750 |
| Q002 | 0.125 | 0.500 | 0.750 |
| Q003 | 0.143 | 0.429 | 0.571 |
| Q004 | 0.091 | 0.364 | 0.455 |
| Q005 | n/a | n/a | n/a |
| all | 0.090 | 0.448 | 0.631 |

### Reciprocal rank

| query | k=1 | k=5 | k=10 |
| --- | ---: | ---: | ---: |
| Q001 | 0.000 | 0.333 | 0.333 |
| Q002 | 1.000 | 1.000 | 1.000 |
| Q003 | 1.000 | 1.000 | 1.000 |
| Q004 | 1.000 | 1.000 | 1.000 |
| Q005 | 0.000 | 0.000 | 0.000 |
| all | 0.600 | 0.667 | 0.667 |

Q001's first relevant chunk is rank 3, so reciprocal rank does not move between k = 5 and k = 10. The chunk that actually states the last published update, `KB-AWS-NEG-003-01`, is rank 7.

## Failures

The near-miss article outranks the article that answers the question. On Q001 the maintenance notice takes ranks 1, 2, and 4. Distances run from 0.2942 to 0.3383 across the first seven chunks, so the 2023 window and the live-status article are close. The limits chunk that says the health article is not that notice never appears.

One half of a two-part query fills the list. Q004 ranks 1 through 4 are the flicker checks. Ranks 5, 6, 9, and 10 are the audio article. The 21-day return policy and the 12-month technician overview are outside the top 10. The return chunk that did come back, `KB-SAM-NEG-002-03`, says the article will not diagnose flicker and will not send a technician. Q003 puts the address-change article in the top slots and never returns the expedited timeline.

Shared words pull the wrong article. "Router" brings firmware. "Project role" brings the permission scheme, which is about who can edit an issue, not who is emailed. "QN90A" brings audio dropouts. Q005 has nothing to retrieve, and the list is still 10 chunks. Its best distance is 0.3632. Q001's rank 10 is 0.3525. A cutoff that dropped the password-reset chunk would sit on top of a list that still contains a real answer, so I would not use one.

## Possible improvements

Ask the two procedures separately when the query has two. I tried the shipping half on its own, expedited service after a destination change. `KB-SHIP-001-01`, the two-to-three-day timeline, came back at rank 2. The combined query had not returned it at all.

I would not raise k to buy recall. Precision goes from 0.520 at k = 5 to 0.360 at k = 10. The extra slots are the audio article, the firmware article, and more of the 2023 notice.

The health article and the maintenance notice would be easier to tell apart if `embedding_text` carried the article topic. I left topic out in Task 3. General service health and the named maintenance event are different topics, and the titles alone were not enough. I am not rebuilding the store in this task.

Q005 needs an empty result, not the nearest neighbors. The store cannot say "nothing in the corpus." The distances are a weak signal, and they overlap the tail of a query that does have an answer.
