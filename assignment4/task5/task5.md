# Task 5 — Write an Initial Prompt

**Code:** `assignment4/task5/summarize_ticket.py`

**Output:** `assignment4/task5/outputs/ticket_5572.json`

**Test ticket:** `5572`

The model is `qwen2.5:1.5b-instruct-q4_K_M` at `http://localhost:11434/api/chat`. Temperature is 0 and the seed is 42. `stream` is false. The request `format` is the JSON Schema for the three fields. I am leaving those settings fixed so a later prompt change is the only thing that moves.

## The ticket

I wanted one body that was more than a line or two, and I did not use any of the ten ticket ids Task 6 assigns. Ticket `5572` is 495 characters. The body says access to software and hardware tools is failing, names a possible cause, and lists steps that already failed.

Only `Body` was sent. `Department`, `Priority`, and `Tags` stayed in the CSV.

```
Dear Support Team, we are encountering occasional access problems with various software and hardware tools. The root cause might be related to network security vulnerabilities. We have tried several solutions such as restarting systems, updating software, and verifying network connections, but the issues still persist. This is causing concern about potential impacts on productivity and security. We would greatly appreciate your help in resolving this matter. Could you please look into this?
```

## The prompt

This is the system message. The user message is the raw body.

```
You write an internal note for a human support agent about one support ticket. You do not route the ticket, invent a fix, or take an action.

The user message is the ticket body. Use only that text. If a detail is not in the body, do not add it.

Reply with a JSON object and nothing else. The object has exactly these fields:
- summary: one or two sentences describing the reported issue.
- customer_request: the action or outcome the customer appears to want.
- missing_information: a list of details needed to understand or act on the request. Use an empty list when nothing is clearly missing.
```

`summarize_ticket` posts that pair of messages and checks the content before returning it. The check requires a JSON object with exactly `summary`, `customer_request`, and `missing_information`. Both strings have to be non-empty. `missing_information` has to be a list of non-empty strings, and an empty list is allowed. `summary` has to be one or two sentences. Anything else raises.

Re-run from the repository root:

```bash
.venv/bin/python assignment4/task5/summarize_ticket.py
```

## The output

The call returned this object, and the check accepted it.

```json
{
  "summary": "Occasional access problems with software and hardware tools are reported, possibly due to network security vulnerabilities.",
  "customer_request": "Resolve the access problems and ensure security is not compromised.",
  "missing_information": []
}
```
