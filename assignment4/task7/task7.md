# Task 7 — Two Prompt Iterations

The model, JSON schema, temperature 0, seed 42, and the ten ticket bodies stayed as they were in Task 6. The only edit in each iteration is the system message. Outputs are in `iteration1/outputs/` and `iteration2/outputs/`. Every output passed the same checker as Task 5. `schema_error` is null on all twenty calls.

Re-run from the repository root:

```bash
.venv/bin/python assignment4/task7/run_iteration.py iteration1
.venv/bin/python assignment4/task7/run_iteration.py iteration2
```

The Task 6 outputs are the baseline for iteration 1. Iteration 1 was rejected, so iteration 2 is compared with Task 6 again, not with iteration 1.

## Iteration 1

**Pattern.** `missing_information` is empty on nine of the ten tickets, including bodies that never give an amount, a date, a document, or which system is affected. On 28571 the list is not empty, and it is filled with the questions the customer is asking. Same field, two ways of getting it wrong. I picked this one because it showed up on every ticket.

**The change.** One bullet. The rest of the prompt is the Task 5 text.

Old:

```
- missing_information: a list of details needed to understand or act on the request. Use an empty list when nothing is clearly missing.
```

New:

```
- missing_information: facts that are not in the ticket and that an agent would need before acting. Name the missing fact, such as an amount, a date, which system is affected, or a document that was not included. Do not put the customer's questions in this list. Use an empty list only when the body already has the details needed to act.
```

**Prompt**

```
You write an internal note for a human support agent about one support ticket. You do not route the ticket, invent a fix, or take an action.

The user message is the ticket body. Use only that text. If a detail is not in the body, do not add it.

Reply with a JSON object and nothing else. The object has exactly these fields:
- summary: one or two sentences describing the reported issue.
- customer_request: the action or outcome the customer appears to want.
- missing_information: facts that are not in the ticket and that an agent would need before acting. Name the missing fact, such as an amount, a date, which system is affected, or a document that was not included. Do not put the customer's questions in this list. Use an empty list only when the body already has the details needed to act.
```

**Outputs**

28907

```json
{"summary": "Billing discrepancy for AWS Management Service usage", "customer_request": "A detailed breakdown of the billed items, usage metrics, and a written explanation for each charge, along with options for invoicing adjustments.", "missing_information": []}
```

28399

```json
{"summary": "Request for guidance on ticketing system and server management improvements.", "customer_request": "Recommendation for a customized ticketing system and enhanced server management protocols.", "missing_information": []}
```

28381

```json
{"summary": "Seeking expert advice on software development project challenges and potential solutions.", "customer_request": "Arrange a consultation session with IT Consulting Service experts to address architectural planning, performance optimization, and server setup issues.", "missing_information": []}
```

28921

```json
{"summary": "Request for significant enhancements to the internal human resources management system to improve user interface design and data analysis capabilities.", "customer_request": "Implement a redesigned user interface and advanced data analysis tools to enhance user experience and efficiency.", "missing_information": []}
```

28736

```json
{"summary": "The user seeks advice on enhancing server management within their organization to improve reliability and efficiency.", "customer_request": "The user requests comprehensive suggestions and best practices for adopting advanced server technologies, integrating these advancements while mitigating risks or minimizing downtime, and ensuring the team is well-equipped to embrace and sustain these modifications.", "missing_information": []}
```

28763

```json
{"summary": "Samsung QLED QN90A TV flickering issue reported by customer", "customer_request": "Seek professional assistance to resolve the flickering issue with the Samsung QLED QN90A TV.", "missing_information": ["date of purchase", "model specifications", "system logs"]}
```

28563

```json
{"summary": "Customer reports persistent print quality issues with Canon PIXMA MG3620 printer and requests an exchange for a new unit.", "customer_request": "Request for an exchange of the faulty printer and clarification on the exchange process and any specific terms.", "missing_information": []}
```

28571

```json
{"summary": "Clarification needed regarding technical specifications and delivery timeline for Cisco Router ISR4331", "customer_request": "Provide detailed information on technical specifications, delivery timeline, and return policy for Cisco Router ISR4331", "missing_information": ["expected delivery time from the order date", "choice of shipping methods", "expedited service options available", "tracking details for dispatched packages", "return policy details"]}
```

28642

```json
{"summary": "Customer requests clarification on AWS scheduled maintenance and potential impact on operations.", "customer_request": "Clarification on the expected timeline, potential windows of reduced functionality, and any critical actions to be taken prior to the maintenance.", "missing_information": []}
```

29206

```json
{"summary": "Request for modifications to Jira workflows to align with updated company policies on ticket prioritization.", "customer_request": "Implement a customized priority field and a feature for dynamic adjustments based on real-time status and project goals.", "missing_information": []}
```

**Impact.** The field I tried to change barely moved. Eight of the nine empty lists are still empty: 28907, 28399, 28381, 28921, 28736, 28563, 28642, and 29206. 28381, 28921, and 29206 are the same object as Task 6.

28763 is the one list that filled in. "date of purchase" is a real gap. "model specifications" is a weak one, because the body already names the QN90A. "system logs" is not something this ticket is missing. Nobody mentioned logs.

28571 still copies the customer's questions into the list. The new sentence said not to do that. It did it anyway, and added tracking to the list.

A few request lines moved even though I did not edit that bullet. 28736 now asks for suggestions, downtime, and training, which is closer to the three questions. 28907 adds the written explanation per charge. 28563 adds the exchange steps. Those are improvements, and they were not the target. 28642 dropped the contingency plans from an otherwise good request. 28399's summary got vaguer.

**Decision.** Revert. The pattern is still there on nine tickets, and the one new list includes a fact the prompt made up. I am not carrying this wording forward. Iteration 2 starts from the original prompt.

## Iteration 2

**Pattern.** The request line keeps the topic and drops the thing the customer asked the agent to do. Task 6 showed this on the consultation (28399), the timeline (28921), the numbered questions and the meeting (28736), the diagnosis steps and the warranty (28763), the exchange steps (28563), and the ask for guidance rather than a build (29206). I left `missing_information` alone because the first wording did not fix it.

**The change.** One bullet, on the original prompt.

Old:

```
- customer_request: the action or outcome the customer appears to want.
```

New:

```
- customer_request: the specific action or reply the customer asked the agent for. If the body asks for a meeting, a timeline, steps, a warranty or repair policy, or answers to listed questions, include those asks. Do not replace them with a general description of the topic.
```

**Prompt**

```
You write an internal note for a human support agent about one support ticket. You do not route the ticket, invent a fix, or take an action.

The user message is the ticket body. Use only that text. If a detail is not in the body, do not add it.

Reply with a JSON object and nothing else. The object has exactly these fields:
- summary: one or two sentences describing the reported issue.
- customer_request: the specific action or reply the customer asked the agent for. If the body asks for a meeting, a timeline, steps, a warranty or repair policy, or answers to listed questions, include those asks. Do not replace them with a general description of the topic.
- missing_information: a list of details needed to understand or act on the request. Use an empty list when nothing is clearly missing.
```

**Outputs**

28907

```json
{"summary": "Billing discrepancy for AWS Management Service usage", "customer_request": "A detailed breakdown of the billed items, usage metrics, and explanations for discrepancies, along with options for invoicing adjustments.", "missing_information": []}
```

28399

```json
{"summary": "Customer requests assistance with establishing a reliable ticketing system and enhancing server management protocols.", "customer_request": "Recommendations for a customized ticketing system, user-friendliness for team members, and insights into refining server administrative processes. Also, availability of a consultation session with a specialist.", "missing_information": []}
```

28381

```json
{"summary": "Seeking expert advice on software development project challenges and potential solutions.", "customer_request": "Arrange a consultation session with IT Consulting Service experts to discuss potential solutions and strategies for our software development project.", "missing_information": []}
```

28921

```json
{"summary": "Request for significant enhancements to the internal human resources management system, focusing on user interface design and data analysis capabilities.", "customer_request": "A redesigned interface that is more user-friendly and visually intuitive, and advanced data analysis tools to facilitate smoother organizational workflows and data-driven decision-making.", "missing_information": []}
```

28736

```json
{"summary": "The user seeks advice on enhancing server management within their IT setup, focusing on adopting advanced technologies, mitigating risks, and ensuring team readiness.", "customer_request": "A meeting or call to discuss the details of the request.", "missing_information": []}
```

28763

```json
{"summary": "Samsung QLED QN90A TV flickering issue reported by customer", "customer_request": "Provide guidance on next steps to diagnose and resolve the flickering issue, including instructions for at-home diagnosis or arranging a qualified technician's assessment. Also, request information about repair policies and warranty coverage for such issues.", "missing_information": []}
```

28563

```json
{"summary": "Customer is experiencing inconsistent print quality with their Canon PIXMA MG3620 printer and requests an exchange for a new unit.", "customer_request": "Initiate the exchange process for a new printer and provide steps and any specific terms or conditions.", "missing_information": []}
```

28571

```json
{"summary": "Clarification needed regarding technical specifications, delivery timeline, and return policy for Cisco Router ISR4331", "customer_request": "Provide technical specifications, delivery timeline, and return policy for Cisco Router ISR4331", "missing_information": []}
```

28642

```json
{"summary": "Customer requests clarification on AWS maintenance schedule and potential impact on operations.", "customer_request": "Provide a detailed timeline and potential windows for reduced functionality or complete outage during the maintenance period.", "missing_information": []}
```

29206

```json
{"summary": "Request for guidance on implementing workflow modifications to accommodate new company policies regarding ticket prioritization in Jira Software 8.20.", "customer_request": "Provide guidance on the best approach for implementing workflow modifications to accommodate new company policies regarding ticket prioritization in Jira Software 8.20.", "missing_information": []}
```

**Impact.** Four request lines now say what the customer asked the agent to do.

- 28399 adds the consultation with a specialist. The summary is unchanged, so the latency is still missing, and the gap list is still empty.
- 28763 now asks for at-home diagnosis or a technician, plus the repair policy and the warranty. That was the whole second half of the ticket, and Task 6 had reduced it to "seek professional assistance." The summary is still a fragment.
- 28563 keeps the exchange and adds the steps and the terms. The summary also says the print quality is inconsistent, which is closer to the streaks and blotches.
- 29206 says "provide guidance" instead of "implement" the two features. The summary names Jira Software 8.20. Feasibility, plugins, documentation, and the meeting are still not in the request. The direction is right.

28907 did not change. 28921 still has no timeline. The bullet told the model to include a timeline when the body asks for one, and this body does.

Regressions:

- 28381 used to name architectural planning, performance optimization, and server setup. The new request says "potential solutions and strategies" and those three areas are gone from the output.
- 28736's request is now only a meeting. The three numbered questions are not in `customer_request`. The summary picked up tools, risk, and team readiness, so some of that text moved rather than disappearing, and the request field itself got narrower.
- 28571 dropped compatibility, unique features, shipping methods, and tracking from the request. The return policy did move into the request, and the old gap list of customer questions is gone. Shipping and tracking are not in the output at all.
- 28642 lost the contingency plans and the prep tasks. Task 6 had both. The summary is a bit better: it no longer says the maintenance is expected to cause an outage.

The empty gap lists did not get better. That was not this change.

**Decision.** Keep. The failure I aimed at got better on 28399, 28763, 28563, and 29206, and those four were the notes that had replaced the ask with the topic. 28763 is the clearest case. I am not treating this as a clean win. 28381, 28736, and 28642 got thinner, and 28921 still has no timeline. I would still rather carry this prompt than the original, because the original's worst request lines were the ones that moved, and I do not get a third edit. The empty `missing_information` lists remain. Iteration 1 already showed that a longer instruction did not fix them.
