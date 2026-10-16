# Task 2 — Retrain and Apply the ML Model

**Class:** `assignment3/task2/ticket_router.py` (`TicketRouter`)

**Split script:** `assignment3/task2/apply_split.py`

**Saved model:** `assignment3/task2/outputs/ticket_router.joblib`

**Predictions:** `assignment3/task2/outputs/validation_predictions.csv`

**Environment:** `.venv` with `assignment3/homework_materials/SIDDESH NATESAN - requirements.txt` (`pandas==3.0.5`, `scikit-learn==1.9.1`, `joblib==1.6.0`).

**How to re-run** (from the repository root):

```bash
.venv/bin/pip install -r "assignment3/homework_materials/SIDDESH NATESAN - requirements.txt"
.venv/bin/python assignment3/task2/apply_split.py
```

The script reads the source CSV and `split_manifest.csv`, fits on the training ids, predicts every validation ticket, and writes the model and the CSV. It fits a second time and checks that both fits recommend the same department on every training row and every validation row. It also saves the model, loads it back, and checks that the loaded copy agrees on the validation routes.

---

## What moved into the class

Homework 2 cleaned the body in Task 1, then fitted the vectorizer on that cleaned text. This homework asks `fit` and `predict` to take the raw body. `clean_body` is the same cleaner, and both methods call it before the vectorizer. Lowercasing stays in the vectorizer, same as before.

`predict` takes one body or a list. One body returns the same dictionary as Homework 2: `recommended_department` and `class_scores`. A list returns one of those dictionaries per body, in the same order. The ten scores are in alphabetical order and sum to 1. The recommended department is the highest score.

## The model

The classifier is the Homework 2 baseline. Logistic regression, `lbfgs`, `C=1`, `class_weight="balanced"`, `random_state=42`, `max_iter=200`. The vectorizer is still word TF-IDF, unigrams and bigrams, `min_df=2`, `max_df=0.95`, no English stop-word list. `class_weight="balanced"` is computed inside this fit, from the canonical training labels only. I did not load the Homework 2 weight file. Those weights belonged to the old training split.

This fit uses 17,524 training tickets. Cleaning changes 1,763 of those bodies. None of them are empty after cleaning. Ticket `28902`, the missing body, is not in this manifest, so there is no blank row to skip. The vocabulary is 56,650 columns. The solver finishes in 92 iterations.

## The split

`apply_split.py` joins the manifest to the source CSV on `ticket_id`. It does not read the Homework 2 cleaned file. A canonical id has to be resolved against the source, so an earlier cleaning step cannot drop a held-out ticket.

Every manifest id is in the source. I keep every training row and every validation row. I do not drop, relabel, dedupe, or sample them. `Priority` and `Tags` are not read. The test split is not loaded into the frame that gets fitted or predicted.

Rows are sorted by `ticket_id` before `fit`. `lbfgs` does not shuffle, and `random_state=42` is set, so the second fit sees the same order. The two fits agreed on all 17,524 training routes and all 3,755 validation routes.

## Predictions

The CSV has 3,755 rows, one per validation ticket, sorted by `ticket_id`. The columns are `ticket_id`, `true_label`, `recommended_department`, and `class_scores`. `true_label` is the source `Department`. `class_scores` is the dictionary from `predict`, written with `json.dumps`. No training id and no test id is in that file.

I am not scoring this file here. The metrics from Task 1 belong in Task 3, computed from this CSV.
