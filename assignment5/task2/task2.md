# Task 2 — Apply the Rubric

I scored the iteration 2 outputs. Those are the accepted Homework 4 summaries. I did not call the model again. Each body is the canonical `Body` from Task 6, unchanged. The five tickets are 28907, 28921, 28763, 28571, and 29206.

The frozen rubric is `rubric.md` in this folder. Task 1 has the rubric as it stood before this pass.

## Rubric changes

Two wording changes. I had already written a score for all five with the Task 1 text. I went back through them after the edits. Nothing moved.

**Customer request, the 1.** Task 1 said a 1 is the main ask, plus "a second ask" missing. That fit 28907, which drops the discounts and keeps the rest. It did not fit the way I was scoring 28571 and 29206. Each of those drops a list of asks, not one leftover question, and both lines still tell the agent what to do. I was not willing to call either a 0. Task 6 on 28736 is a 0, because the line never says the action. 28571 does say the action. I changed the 1 criterion to "one or more specific asks from the body are missing," and I put 28571 on that line. The 0 criterion now says that dropping several sub-questions is still a 1 when the action is named.

**Summary, the 1.** The Task 1 examples were fragments, plus 28381. 29206's accepted summary is a full sentence. It names Jira Software 8.20 and ticket prioritization, and it leaves out the custom priority field, the dynamic adjustments, and the new statuses and transitions. I added that sentence to the 1 criterion so a grammatical summary can still be a 1. 28921 stayed a 2. That summary names the interface and the data analysis tools, which is the change they asked for.

I also wrote down a grounding call I had to make on 28907. "Explanations for discrepancies" is shorter than "a written explanation for each charge." It is the same claim. I put that under score 2, and I left the thinness on the request score. I did not want a short paraphrase to count as "might" becoming "expected."

I did not add a dimension. I did not change the 0–2 scale.

The gap lists were the place I almost softened the rubric. All five accepted outputs score 0. A 1 would have separated them, and it would have been the wrong score. The 1 is a list that contains a real gap and is incomplete. These lists are empty. 28907 still has no amounts. 28763 still has no purchase date. Lowering the bar would hide the failure Homework 4 already settled on. I left the criterion, and I added one line: an empty list does not get a 1.

This is the rubric for the later RAG comparison.

## Scores

| ticket_id | Grounded | Summary | Customer request | Missing information | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| 28907 | 2 | 1 | 1 | 0 | 4 |
| 28921 | 2 | 2 | 1 | 0 | 5 |
| 28763 | 2 | 1 | 2 | 0 | 5 |
| 28571 | 2 | 1 | 1 | 0 | 4 |
| 29206 | 2 | 1 | 1 | 0 | 4 |

The total is the four scores added. The gap list is 0 on every ticket, so the totals sit at 4 or 5. Grounded is 2 on every ticket. The spread is the summary and the request line.

## 28907 — Billing and Payments

```json
{
  "summary": "Billing discrepancy for AWS Management Service usage",
  "customer_request": "A detailed breakdown of the billed items, usage metrics, and explanations for discrepancies, along with options for invoicing adjustments.",
  "missing_information": []
}
```

**Grounded: 2.** AWS Management Service, the discrepancy, the breakdown, the usage metrics, the explanations, and the invoicing adjustments are all in the body. Nothing is firmer than what they wrote. The request line shortens "a written explanation for each charge" to "explanations for discrepancies." That is the same claim, so it stays a 2 here.

**Summary: 1.** There is no period, and the line is a label. It drops the last quarter, the internal audit, and that the bill was higher than expected. The topic is the right one, which is why it is not a 0.

**Customer request: 1.** The breakdown, the metrics, the explanations, and the adjustment options are the asks I wanted this field to keep. The body also asks whether discounts or other billing mechanisms were available and not applied. That question is not in the line. The closing offer to get on a call is not the miss I am scoring. The discounts are.

**Missing information: 0.** The list is empty. The body never says which charges disagree or by how much. The statement date is the placeholder `date`, and the account is `acc_num`. An agent cannot review the bill from this text.

## 28921 — Human Resources

```json
{
  "summary": "Request for significant enhancements to the internal human resources management system, focusing on user interface design and data analysis capabilities.",
  "customer_request": "A redesigned interface that is more user-friendly and visually intuitive, and advanced data analysis tools to facilitate smoother organizational workflows and data-driven decision-making.",
  "missing_information": []
}
```

**Grounded: 2.** The HR system, the interface, and the data analysis tools are in the body. "Smoother organizational workflows" and "data-driven decision-making" are the customer's own wording for why they want the change. The note does not add a module, a report, or a date.

**Summary: 2.** One sentence, and it names the system and both enhancement areas. The navigation bottlenecks are the reason they give, and the timeline is an ask for the agent. I am not taking those out of this score. 29206 is the contrast on this dimension: that summary names the area and drops the actual change. This one has the change in the sentence.

**Customer request: 1.** The redesigned interface and the analysis tools are what they want built, and both are in the line. The body then asks for a plan and a timeline, and it says to treat the request as urgent. None of that is in the field. I left it at 1 because the enhancement itself is stated. A 0 would be a line that never says what they want done.

**Missing information: 0.** The list is empty. "Various modules" never gets named, and the body does not say which reports the HR team cannot produce. Those are what an agent would need before scoping the change.

## 28763 — Product Support

```json
{
  "summary": "Samsung QLED QN90A TV flickering issue reported by customer",
  "customer_request": "Provide guidance on next steps to diagnose and resolve the flickering issue, including instructions for at-home diagnosis or arranging a qualified technician's assessment. Also, request information about repair policies and warranty coverage for such issues.",
  "missing_information": []
}
```

**Grounded: 2.** The set is the QN90A, the symptom is flickering, and the request line follows the two asks in the second half of the body. The note does not pick a cause. "Also, request information" is a clumsy way to phrase the warranty ask. The content is still theirs. I am not docking grounded for the phrasing.

**Summary: 1.** It is a subject line. It has the product and the flicker, and it stops. The body says the flicker is intermittent and getting worse, and that cables, power, brightness, and a software refresh did not help. None of that is in the summary.

**Customer request: 2.** This is the line iteration 2 fixed. It asks for at-home diagnosis or a technician, and for the repair policy and the warranty. Task 6 had reduced the same body to "seek professional assistance." I am not requiring the summary's missing troubleshooting to also appear here.

**Missing information: 0.** The list is empty. There is no purchase date and no serial, and the body never says whether the set is still under warranty. They asked for the warranty rules because that status is not in the ticket. Iteration 1 had put "date of purchase" in the list and then added "system logs." The accepted output went back to empty. Empty is a 0, not a 1.

## 28571 — Sales and Pre-Sales

```json
{
  "summary": "Clarification needed regarding technical specifications, delivery timeline, and return policy for Cisco Router ISR4331",
  "customer_request": "Provide technical specifications, delivery timeline, and return policy for Cisco Router ISR4331",
  "missing_information": []
}
```

**Grounded: 2.** The router, the specifications, the delivery timeline, and the return policy are all questions in the body. The note adds no spec and no ship date. Task 6 had stuffed the customer's questions into `missing_information`. Those questions were in the body, so that was a field error, not an invented fact. The accepted output dropped the list. Grounded stays a 2 either way.

**Summary: 1.** No period. The line does name the three headlines, specifications, delivery, and the return policy, which is more than the Task 6 summary. It is still a fragment, so it stays a 1. It is not a 0. The issue in the summary is the issue in the email.

**Customer request: 1.** "Provide technical specifications, delivery timeline, and return policy" is an action, which is why this is not a 0. The body asks for more than those three headlines. Under specifications it asks about effectiveness, compatibility, and unique features. Under delivery it asks for the time from the order date, the shipping methods, expedited service, tracking, and the durations for regular and faster service. The return policy is the one piece Task 6 had left out of this field, and iteration 2 put it back. The shipping list is still gone. This is the ticket that made me widen the 1 criterion from "a second ask" to "one or more."

**Missing information: 0.** The list is empty. Task 6 had filled it with the customer's questions, which was the other way to score a 0. Iteration 2 deleted that list and did not put a real gap in its place. The body never says how many routers, or where they ship. A delivery time from the order date cannot be answered without a destination. An empty list here is still a 0.

## 29206 — Technical Support

```json
{
  "summary": "Request for guidance on implementing workflow modifications to accommodate new company policies regarding ticket prioritization in Jira Software 8.20.",
  "customer_request": "Provide guidance on the best approach for implementing workflow modifications to accommodate new company policies regarding ticket prioritization in Jira Software 8.20.",
  "missing_information": []
}
```

**Grounded: 2.** Jira Software 8.20, the workflow changes, the prioritization policy, and the request for guidance are in the body. The note does not invent a plugin, a timeline, or a new status. The request line is almost the same sentence as the summary. Repetition is not an added fact.

**Summary: 1.** It is one sentence, and the topic is right, so the fragment rule is not what fails it. The body describes the change: a custom priority field lined up with their matrix, dynamic adjustments from real-time status and project goals, and new statuses and transition conditions. The summary says "workflow modifications" and "ticket prioritization" and stops. That is the 28381 pattern, a grammatical sentence that names the area. I added 29206 to the 1 criterion for this reason. The score I had given it before the edit was already 1.

**Customer request: 1.** "Provide guidance on the best approach" is the sentence they wrote, and it is the right direction. Task 6 had said "implement" the two features and dropped the guidance. Iteration 2 flipped that, and it lost the features on the way. The body then asks about feasibility, timelines, configuration help, plugins, documentation from earlier work, and a time to talk. None of those are in the field. The line still names the action, so it is a 1 and not a 0.

**Missing information: 0.** The list is empty. The "updated prioritization matrix" is named and never described. Current workflows are not described either. An agent cannot judge feasibility from this text.
