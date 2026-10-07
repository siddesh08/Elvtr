# Assignment 2

Week 2 homework: clean the support-ticket file, split it, turn the ticket text into features, and train a baseline department router.

Run these from the repository root, in order. Task 2 reads the cleaned CSV, Task 3 reads that file plus the split manifest, and Task 4 trains on the training split.

## Setup

Week 1 already created `.venv`. If it is missing:

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r assignment2/homework_materials/requirements.txt
```

`requirements.txt` pins `pandas==3.0.5`, `scikit-learn==1.9.1`, and `joblib==1.6.0` for Python 3.14.7. I ran the scripts with Python 3.12.13, same as Week 1.

The source CSV stays where it is. Nothing below overwrites it.

`assignment2/homework_materials/SIDDESH NATESAN - support_tickets - SIDDESH NATESAN - support_tickets.csv`

## Scripts

```bash
.venv/bin/python assignment2/task1/clean_tickets.py
.venv/bin/python assignment2/task2/split_tickets.py
.venv/bin/python assignment2/task2/verify_split.py
.venv/bin/python assignment2/task3/preprocess.py
.venv/bin/python assignment2/task4/ticket_router.py
```

`verify_split.py` only checks the manifest. `split_tickets.py` already runs those checks before it exits. I still run the verifier on its own.

## Outputs

- Task 1 cleaned tickets: `assignment2/task1/outputs/cleaned_support_tickets.csv`. Notes in `assignment2/task1/task1.md`.
- Task 2 manifest (`ticket_id`, `split`): `assignment2/task2/outputs/split_manifest.csv`. Notes in `assignment2/task2/task2.md`.
- Task 3 matrices, indexes, vectorizer, and class weights: `assignment2/task3/outputs/`. Notes in `assignment2/task3/task3.md`.
- Task 4 model: `assignment2/task4/outputs/ticket_router.joblib`. Notes in `assignment2/task4/task4.md`.

Task 4 fits on the training bodies only. It does not score validation or test.

After the model file exists, this is how I check one new body. From the repository root, with the venv Python:

```python
import sys

sys.path.insert(0, "assignment2/task4")
from ticket_router import TicketRouter

router = TicketRouter.load("assignment2/task4/outputs/ticket_router.joblib")
print(router.predict("The vpn client disconnects every few minutes."))
```
