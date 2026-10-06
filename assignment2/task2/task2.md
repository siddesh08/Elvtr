# Task 2 — Split the Data

**Cleaned file (not modified):** `assignment2/task1/outputs/cleaned_support_tickets.csv`

**Manifest:** `assignment2/task2/outputs/split_manifest.csv`

**Environment:** `.venv` with `assignment2/homework_materials/requirements.txt` (`pandas==3.0.5`, `scikit-learn==1.9.1`, `joblib==1.6.0`). This task only imports `pandas`. The assignment is written out by hand. I did not call `train_test_split` or any other library splitter.

**How to re-run** (from the repository root):

```bash
.venv/bin/pip install -r assignment2/homework_materials/requirements.txt
.venv/bin/python assignment2/task2/split_tickets.py
.venv/bin/python assignment2/task2/verify_split.py
```

`split_tickets.py` writes the manifest and runs the same checks. `verify_split.py` reads the manifest back and checks it again, including that a fresh run with the saved seed reproduces every row.

The manifest has two columns, `ticket_id` and `split`. `split` is `train`, `validation`, or `test`. It is sorted by `ticket_id` and has one row for each of the 29,651 cleaned tickets.

---

## Proportions

I used 80% train, 10% validation, and 10% test, measured in tickets, inside each department.

This file has 29,651 tickets. Ten percent is about 3,000 tickets, which is enough to compare models on the validation split and still leave a test split for Homework 3. A 98/1/1 split is what you do when the file already has millions of rows and 1% is still a large count. Here 1% of General Inquiry would be about 4 tickets. That is too few to notice if that department disappeared from a holdout.

The realized split is:

| Split | Tickets | Share |
| --- | ---: | ---: |
| train | 23,721 | 80.00% |
| validation | 2,968 | 10.01% |
| test | 2,962 | 9.99% |

It is not exact, because a repeated body is kept in one split. The largest repeated body is 4 tickets (`Assistance Required`), so a group can miss a target by only a few rows. Across the whole file that rounds to a hundredth of a percent.

The same ratio shows up inside each department. General Inquiry is the smallest class, 419 tickets, and it landed at 335 / 42 / 42. Every department is within about 0.1 percentage point of 80/10/10, and every department has at least 42 tickets in validation and 42 in test.

| Department | Train | Validation | Test |
| --- | ---: | ---: | ---: |
| Billing and Payments | 2,414 | 302 | 301 |
| Customer Service | 3,585 | 448 | 449 |
| General Inquiry | 335 | 42 | 42 |
| Human Resources | 454 | 57 | 57 |
| IT Support | 2,800 | 350 | 350 |
| Product Support | 4,433 | 555 | 551 |
| Returns and Exchanges | 1,172 | 147 | 148 |
| Sales and Pre-Sales | 708 | 89 | 88 |
| Service Outages and Maintenance | 926 | 116 | 115 |
| Technical Support | 6,894 | 862 | 861 |

I am not using the test split to choose a model. Scoring it more than a couple of times while I am still changing the model would turn it into a second validation set. Homework 3 is the evaluation.

---

## Assignment strategy

The thing I do not want to split is an exact cleaned `Body`. There are 25,055 distinct bodies and 4,594 of them occur more than once (9,190 rows). Cleaning did not change that distinct count, so the copies were already exact and they are still exact. If one copy is in train and another is in test, the test score is partly "have I seen this paragraph before."

There is no customer id, account id, or timestamp. A time split would need an arrival time, and the dataset card does not give one. I am not going to treat `ticket_id` as time. A customer split has nothing to group on. The dependency that is actually in the file is the repeated body, so that is the group.

Inside a department, the rule is:

1. Build one group per exact `Body`. Every ticket in the group is assigned together.
2. The department I count the group under is the department on the lowest `ticket_id` in the group. When every copy has the same department, that is just the department. When they disagree, I still need one bucket so the group is not broken.
3. Sort the groups in that department by the lowest `ticket_id`, then shuffle them with `random.Random(42)`.
4. Give the next group to whichever of train, validation, or test is furthest below its target count (80%, 10%, 10% of the tickets in that department). If two splits are equally short, train wins, then validation, then test.

Tickets `7907` and `22776` are the same Technical Support text, and both are in train. Tickets `15763` and `20538` are the same Billing and Payments text, and both are in validation. Tickets `9719` and `26089` are another Billing pair, both in test.

Nine bodies disagree about the department. They are the short ones from Task 1. I did not pick a "true" label. They stay together, and the lowest `ticket_id` only decides which department's quota they count against. Twenty rows is not enough to move the table above.

| Body | Tickets | Counted under | Split |
| --- | --- | --- | --- |
| Assistance Required | `5928`, `9070`, `19516`, `21596` | Product Support | train |
| Could you provide details on securing medical data? | `7516`, `20207` | Customer Service | train |
| Could you provide more details? | `9520`, `17884` | Product Support | train |
| In need of assistance | `6809`, `16490` | Product Support | test |
| Offer insights into digital strategies | `6367`, `17792` | Sales and Pre-Sales | train |
| Seek Assistance | `7307`, `19871` | Returns and Exchanges | train |
| Seeking Assistance | `6622`, `24675` | Product Support | test |
| Seeking assistance | `2761`, `17244` | Product Support | test |
| Seeking information | `11054`, `24872` | Billing and Payments | train |

Under seed 42, none of those nine landed in validation. I am not changing the seed to put one there. The texts are too thin to be a useful validation case, and moving the seed would reshuffle every department.

Ticket `28902` has an empty body, so it is its own group. It is in train, under Product Support. Task 3 should skip it when building features. It stays in the manifest so the id is not dropped.

---

## Reproducibility parameters

| Parameter | Value |
| --- | --- |
| Train / validation / test shares | 0.80 / 0.10 / 0.10, within each department, by ticket count |
| Group key | exact cleaned `Body` |
| Department for a mixed group | department on the lowest `ticket_id` |
| Order before the shuffle | lowest `ticket_id` in the group |
| Generator | `random.Random(42)`, a new one for each department |
| Tie break | `train`, then `validation`, then `test` |

The seed is fixed so the manifest does not move while I am on the later tasks. Running `split_tickets.py` twice in one process produces the same frame. `verify_split.py` builds the assignment again from the cleaned file and checks it against the CSV on disk.

The checks also require:

- The manifest columns are `ticket_id` and `split`, with each cleaned `ticket_id` once and no extras.
- Every `split` value is `train`, `validation`, or `test`.
- Each share is within 1 percentage point of its target.
- No `Body` appears in more than one split.
- Every department has at least 20 rows in each split. The smallest holdout cell is 42, so 20 is a floor that would fail if a rare department had been left out, without being so tight that it only passes for this seed.
