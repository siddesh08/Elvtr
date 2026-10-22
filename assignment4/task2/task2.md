# Task 2 — Run a Controlled Classifier Iteration

**Code:** `assignment4/task2/ticket_router.py`, `assignment4/task2/apply_split.py`

**Candidate model:** `assignment4/task2/outputs/ticket_router.joblib`

**Candidate predictions:** `assignment4/task2/outputs/validation_predictions.csv`

**Baseline, left as it was:** `assignment3/task2/outputs/ticket_router.joblib` and `assignment3/task2/outputs/validation_predictions.csv`

The test split was not read.

## The change

Task 1's cue-word category is the one I can aim at. On 19 of the 48 tickets I read, one n-gram with a large coefficient was the biggest push toward the wrong support department: `network` 2.12, `website` 2.06, `server` 1.83, `crashes` 2.21, `breach` 1.12, `campaign` 1.16, `api` 1.30, and the others listed in Task 1. Stripping those words out of the text would also strip them from tickets that belong in that department. The cleaner is already the Homework 2 cleaner. I left it alone.

The one change is `LogisticRegression` `C=0.1` instead of `C=1.0`. Same solver (`lbfgs`), same `class_weight="balanced"`, same `random_state=42`, same `max_iter=200`, same word TF-IDF (unigrams and bigrams, `min_df=2`, `max_df=0.95`). Smaller `C` is a stronger L2 penalty, so a single coefficient has less room to outvote the rest of the body. I did not try a second value.

Training is the Homework 3 procedure. 17,524 training tickets, sorted by `ticket_id`, raw bodies, canonical labels. 3,755 validation tickets predicted. A second fit agreed on every training route and every validation route. Vocabulary is still 56,650. Cleaning still changes 1,763 training bodies, and none are empty. The solver finished in 21 iterations. Homework 3 took 92 at `C=1.0`.

Re-run from the repository root:

```bash
.venv/bin/pip install -r "assignment3/homework_materials/SIDDESH NATESAN - requirements.txt"
.venv/bin/python assignment4/task2/apply_split.py
```

## The 19 cue-word tickets

All 19 were wrong under Homework 3. Two are right under `C=0.1`. Ten are still on the same wrong desk. Seven moved to a different wrong desk.

| ticket_id | True label | Homework 3 | C=0.1 |
| ---: | --- | --- | --- |
| 54 | Technical Support | IT Support | Service Outages and Maintenance |
| 313 | Technical Support | Product Support | Technical Support |
| 432 | Technical Support | IT Support | Service Outages and Maintenance |
| 455 | Technical Support | Product Support | Product Support |
| 460 | Technical Support | IT Support | IT Support |
| 494 | IT Support | Product Support | Technical Support |
| 583 | Technical Support | Product Support | Product Support |
| 820 | Technical Support | IT Support | IT Support |
| 1002 | IT Support | Technical Support | Technical Support |
| 1059 | Technical Support | Product Support | Technical Support |
| 1074 | Product Support | Technical Support | Service Outages and Maintenance |
| 1134 | Technical Support | IT Support | IT Support |
| 1158 | Technical Support | IT Support | IT Support |
| 1187 | Product Support | Technical Support | Technical Support |
| 1227 | Technical Support | IT Support | Service Outages and Maintenance |
| 1250 | Product Support | Technical Support | Human Resources |
| 1262 | Product Support | IT Support | IT Support |
| 1353 | IT Support | Technical Support | Technical Support |
| 2020 | Product Support | IT Support | Technical Support |

313 and 1059 are the two that flipped. In Task 1 their margins were 0.006 and 0.024. They were already ties. 820 is the short website ticket, margin 0.223, and it is still IT Support. 1353 is the crashes ticket, margin 0.215, and it is still Technical Support. Shrinking the coefficient did not make the named product win on the tickets where one word had actually run away with the score.

The weights did shrink. On the predicted department from Task 1, `network` went from 2.12 to 0.59, `website` from 2.06 to 0.43, `crashes` from 2.21 to 0.53, `breach` from 1.12 to 0.31, `api` from 1.30 to 0.39. The same penalty hit words the baseline was right to trust. `billing` went from 13.27 to 5.01. `service` went from 7.52 to 3.34. `outage` went from 6.04 to 2.44.

## Validation metrics

Same definitions as Homework 3. Accuracy is correct validation tickets over 3,755. Macro recall and macro F1 are unweighted means of the ten departments.

| | Homework 3 | C=0.1 | Change |
| --- | ---: | ---: | ---: |
| Correct | 1,769 | 1,308 | -461 |
| Accuracy | 0.471 | 0.348 | -0.123 |
| Macro recall | 0.535 | 0.418 | -0.117 |
| Macro F1 | 0.481 | 0.316 | -0.164 |

1,433 validation tickets changed desk. 149 tickets the baseline missed are now correct. 610 tickets the baseline had right are now wrong.

| Department | Baseline F1 | C=0.1 F1 | Baseline recall | C=0.1 recall |
| --- | ---: | ---: | ---: | ---: |
| Billing and Payments | 0.752 | 0.684 | 0.742 | 0.679 |
| Customer Service | 0.391 | 0.244 | 0.382 | 0.211 |
| General Inquiry | 0.467 | 0.180 | 0.604 | 0.528 |
| Human Resources | 0.516 | 0.221 | 0.563 | 0.394 |
| IT Support | 0.396 | 0.256 | 0.430 | 0.203 |
| Product Support | 0.406 | 0.233 | 0.355 | 0.160 |
| Returns and Exchanges | 0.388 | 0.285 | 0.476 | 0.324 |
| Sales and Pre-Sales | 0.428 | 0.239 | 0.649 | 0.667 |
| Service Outages and Maintenance | 0.573 | 0.379 | 0.703 | 0.608 |
| Technical Support | 0.492 | 0.442 | 0.450 | 0.408 |

The support-trio cells, which were the Task 1 slice:

| True to predicted | Homework 3 | C=0.1 |
| --- | ---: | ---: |
| Technical Support to IT Support | 160 | 86 |
| Product Support to Technical Support | 152 | 178 |
| Technical Support to Product Support | 123 | 61 |
| IT Support to Technical Support | 105 | 117 |
| Product Support to IT Support | 73 | 42 |
| IT Support to Product Support | 36 | 16 |

Those six cells add to 649 before and 500 after. Of the original 649, 74 are now correct, 387 are still wrong inside the trio, and 188 left the trio for a third wrong department. Service Outages took 47 of those 188. The smaller cell count is not 149 fixes.

## Improvements

Two of the 19 cue-word tickets are now on the right desk, 313 and 1059. Both were already within a few hundredths.

Sales and Pre-Sales recall moved from 0.649 to 0.667, 74 true positives to 76. That is the only per-department recall that rose. Precision on that department fell from 0.319 to 0.146, so its F1 still fell, 0.428 to 0.239.

Inside the trio, Technical Support to IT Support dropped by 74 and Technical Support to Product Support dropped by 62. Some of that drop is the 74 real fixes in the wider 649. A lot of it is tickets leaving for Service Outages, General Inquiry, or Sales.

## Regressions

Macro F1 fell from 0.481 to 0.316. Accuracy fell from 0.471 to 0.348. Every department's F1 fell. Macro recall fell with them.

IT Support recall fell from 0.430 to 0.203, and Product Support recall fell from 0.355 to 0.160. Those are the departments the cue words were supposed to stop stealing from. They lost more of their own tickets than they gained back. The other direction got worse too: Product Support to Technical Support rose from 152 to 178, and IT Support to Technical Support rose from 105 to 117.

The small departments lost precision. General Inquiry precision fell from 0.381 to 0.109 and its F1 from 0.467 to 0.180. Human Resources precision fell from 0.476 to 0.154 and its F1 from 0.516 to 0.221. Once `billing`, `service`, and `outage` were pulled down with everything else, more tickets spilled into the departments that do not have a word that strong.

On the 19 tickets this change was for, 7 are now wrong in a new way. 54, 432, 1074, and 1227 went to Service Outages. 1250 went to Human Resources. 494 and 2020 went to Technical Support. None of the shared-wording 21 became correct. None of the 8 non-fault tickets became correct. Seven of those 8 moved to Sales, General Inquiry, or Customer Service.

## Decision

Revert. Homework 3 stays the router.

The primary comparison metric is macro F1, with accuracy next to it. Both got worse, by 0.164 and 0.123. The category I targeted went from 0 of 19 correct to 2 of 19, and those two were coin flips before the change. The coefficient shrink did what the penalty is supposed to do, and it did it to every department at once, including Billing and Service Outages, which were the departments the baseline had actually separated. I am not adopting `C=0.1`. The candidate model and its validation predictions stay in this folder so the later holdout comparison has both fits. I am not refitting anything off the test set, and I have not opened it.
