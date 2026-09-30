# Elvtr

Week 1 homework: acquire, inspect, and augment a public support-ticket dataset so a new ticket can be routed to the right support team.

Files for this assignment are under `assignment1/`.

## Setup and scripts

Clone the repository, then from the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r assignment1/homework_materials/requirements.txt
.venv/bin/python assignment1/task2/profile_dataset.py
.venv/bin/python assignment1/task3/generate_synthetic.py
```

`requirements.txt` lists `pandas==3.0.5` for Python 3.14.7. These scripts were run with Python 3.12.13.

- Task 2 report: `assignment1/task2/outputs/profile_report.md`
- Task 3 tickets: `assignment1/task3/outputs/synthetic_tickets.csv`
