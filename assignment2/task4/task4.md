# Task 4 — Build an ML Baseline

**Class:** `assignment2/task4/ticket_router.py` (`TicketRouter`)

**Saved model:** `assignment2/task4/outputs/ticket_router.joblib`

**Environment:** `.venv` with `assignment2/homework_materials/requirements.txt` (`pandas==3.0.5`, `scikit-learn==1.9.1`, `joblib==1.6.0`).

**How to re-run** (from the repository root):

```bash
.venv/bin/pip install -r assignment2/homework_materials/requirements.txt
.venv/bin/python assignment2/task4/ticket_router.py
```

`fit` trains the vectorizer and the logistic regression on the training split. `predict` takes one ticket `Body` and returns a dictionary with `recommended_department` and `class_scores`, the same two keys as `ml_baseline_output.json`. `save` and `load` use joblib. The script sorts the training rows by `ticket_id`, fits twice, and checks that the second fit predicts the same department for every training row. It also saves the model, loads it back, and checks that the loaded copy agrees on the first training ticket.

I did not score the validation or test splits. Homework 3 is the evaluation. The number below is training-set accuracy only.

---

## Text featurization

The vectorizer is the one from Task 3: word TF-IDF, unigrams and bigrams, lowercased, `min_df=2`, `max_df=0.95`, no English stop-word list. `fit` trains it on the training bodies. I do not load `assignment2/task3/outputs/vectorizer.joblib` into this class, because this `fit` is supposed to train the preprocessor itself. With the same rows and the same settings the vocabulary comes out to the same 66,275 columns.

The input is `Body` only, for the same reason as Task 3. Ticket `28902` has an empty body and is not in the fit. That leaves 23,720 training tickets.

---

## Model

I use logistic regression (`LogisticRegression`, solver `lbfgs`, `C=1`). It is a linear model, so it is cheap on a sparse TF-IDF matrix: this fit finishes in 95 iterations. `predict_proba` gives one score per department, and those scores sum to 1, which is the shape of the example file. The recommended department is the highest score. The ten keys are written in alphabetical order, matching the example.

`class_weight="balanced"` is the Task 3 rule, `training rows / (10 * rows in that department)`, applied only while fitting. Validation and test rows are not involved. I did not tune `C`. A different `C` would be me fitting the model to the validation split, and this homework is only asking for a baseline.

`random_state=42` is set on the classifier. `lbfgs` does not shuffle rows, so the fixed order is the `ticket_id` sort before `fit`. Two fits in one run produced the same predicted department on all 23,720 training rows.

---

## Training accuracy

The model predicts the correct department for **18,464 of 23,720** training records, which is **77.84%**.

That number is the share of training rows whose predicted label matches `Department`. It is not a holdout score. Duplicate bodies that share a label are easy to get right once, because both copies were in the fit. The balanced weights also mean the solver is not trying to maximize this percentage. A miss on General Inquiry costs more during training than a miss on Technical Support, so some majority-class rows are allowed to be wrong. I would not use 77.84% as the routing quality. That measurement belongs on the test split, later, and only a few times.
