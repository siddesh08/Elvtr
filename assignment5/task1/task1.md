# Task 1 — Rubric for the Ticket Summaries

The outputs I am judging are the Homework 4 ticket summaries. The accepted prompt is iteration 2. The model is `qwen2.5:1.5b-instruct-q4_K_M`, temperature 0, seed 42. Each output is the three fields: `summary`, `customer_request`, and `missing_information`.

I took the dimensions from the Task 6 pass and the two iterations. Four things kept showing up.

The gap list was empty on nine of the ten tickets. Bodies still left out an amount, a date, a document, or which system is affected, and the list came back empty anyway. The one list that was not empty, ticket 28571, was filled with the questions the customer is asking.

The request line kept the topic and dropped the thing aimed at the agent. A meeting, a timeline, diagnosis steps, a warranty or repair policy, the numbered questions.

Three summaries are fragments. 28907, 28763, and 28571. Iteration 2 did not turn them into sentences.

I did not see a made-up department or a made-up fix on the Task 6 pass. The wording still slipped once. On 28642 the body says the maintenance might cause a brief outage, and the summary says it is expected to. Iteration 1 also put "system logs" on 28763. Nobody mentioned logs.

I am not scoring the JSON schema. The checker passed every call, and it also passed the fragments, so sentence shape sits in the summary score.

The scale on each dimension is 0, 1, or 2. Yes/no would flatten the notes I kept marking "partly" in Homework 4.

I will apply this in Task 2 to 28907, 28921, 28763, 28571, and 29206. If a ticket does not fit a score, I will change the criterion and re-score the earlier tickets before I freeze the rubric.

## Grounded in the body

**What it measures.** Whether the three fields stay inside the ticket body. The prompt says to use only that text. A cause, a product, a fix, or a stronger claim than the customer made counts as added.

**Scale.** 0, 1, or 2.

**Criteria.**

- 2. Every specific claim is in the body. A paraphrase is fine. On 28563, "print quality issues" stands in for streaks and blotches, and that does not add a fact.
- 1. The topic matches the body, and one claim is firmer or vaguer than what the customer wrote. 28642 is the case I have. "Might" became "expected."
- 0. The note states something the body does not say. "System logs" on iteration 1 of 28763 is a 0. So is a department, a fix, or a product the customer did not name.

Placeholders such as `acc_num`, `date`, and `tel_num` are in the body. Copying them is not an invention.

The customer's own questions are in the body too. Putting those questions in `missing_information` is the wrong field. It is not a grounding miss. That failure is scored on the gap list.

## Summary

**What it measures.** Whether `summary` is one or two sentences, and whether those sentences say what the issue is. A subject line fails this even when the topic is right. A grammatical sentence that only names the area, and leaves out the concrete problem, also fails it.

**Scale.** 0, 1, or 2.

**Criteria.**

- 2. One or two sentences, and the summary alone is enough to know the reported issue. 28563 is the one I would score a 2. It is one sentence, it names the Canon PIXMA MG3620, the print quality, and the exchange.
- 1. The topic is right, and the summary is a fragment or it drops the part that makes this ticket this ticket. 28907 is "Billing discrepancy for AWS Management Service usage." That is a label. It drops the last quarter and that the bill was higher than expected. 28763 is "Samsung QLED QN90A TV flickering issue reported by customer." It names the set and the flicker and says nothing about the flicker getting worse, or about cables, power, brightness, and the software refresh already failing. 28571 has no period. 28381 is one sentence and still too broad: "software development project challenges," with architectural planning, performance, and server setup left out.
- 0. The summary describes a different problem than the one in the body. None of the ten Task 6 summaries were this far off. I am leaving the score in the rubric so a later output can land here.

## Customer request

**What it measures.** Whether `customer_request` is the specific action or reply the customer asked the agent for. Iteration 2 was the edit aimed at this. The old failure was a request line that restates the topic, or the outcome the customer hopes for, and leaves out the ask. If the body asks for a meeting, a timeline, steps, a warranty or repair policy, or answers to listed questions, those belong in this field.

**Scale.** 0, 1, or 2.

**Criteria.**

- 2. The line has the asks that are aimed at the agent. Task 6 on 28642 is the shape I want: the timeline, the outage windows, contingency plans, and the prep tasks. Iteration 2 on 28763 is the same shape after the fix. Diagnosis steps or a technician, plus the repair policy and the warranty. Task 6 on that ticket had reduced all of that to "seek professional assistance."
- 1. The main ask is there, and a second ask from the body is missing. 28907 keeps the breakdown, the usage metrics, the written explanations, and the invoicing adjustments, and it drops the question about discounts that were not applied. 28921 keeps the redesigned interface and the data analysis tools, and it never asks for the plan or the timeline. The body asks for both, and it marks the request urgent. 29206 in iteration 2 says "provide guidance," which is the right direction, and it still leaves out feasibility, plugins, documentation, and the meeting.
- 0. The line describes the topic and does not say what they asked the agent to do. Task 6 on 28736 copies the "we intend to" sentence about advanced server technologies. The three numbered questions and the meeting are not in the field. Task 6 on 29206 says "implement" the custom priority field and the dynamic adjustments. The body asked for guidance on how to do that.

A detail can be missing here and still appear in the summary. I score the request field on its own. 28736 in iteration 2 put tools, risk, and team readiness into the summary, and the request shrank to a meeting. The summary does not rescue the request score.

## Missing information

**What it measures.** Whether `missing_information` lists facts that are not in the ticket and that an agent would need before acting. Empty is allowed when the body already has those facts. The field has two failure modes, and I saw both. An empty list when an amount, a date, a document, or the affected system was never given. A filled list whose entries are the questions the customer is asking the company.

**Scale.** 0, 1, or 2.

**Criteria.**

- 2. The entries are missing facts, and the list covers the ones that block an agent from acting. Or the list is empty and the body really does have what the agent needs. I did not have a 2 on the Task 6 pass. The bodies are long, and they still leave a gap.
- 1. The list is the right kind of item, and it is incomplete or mixed. Iteration 1 on 28763 is the mix I have. "Date of purchase" is a real gap. "Model specifications" is weak, because the body already names the QN90A. "System logs" is not a gap in this ticket. That third entry is also a 0 on grounded. This dimension only asks whether the list is doing its job.
- 0. Either the list is empty and the body is missing something an agent needs, or the entries are the customer's questions, or the entries are invented and there is no real gap in the list. Empty on 28907 is a 0. The body never says which charges disagree or by how much, the statement date is the placeholder `date`, and the account is `acc_num`. An agent cannot review the bill from that text. The Task 6 list on 28571 is a 0 for the other reason. "Expected delivery time," "shipping methods," "expedited service," and "return policy" are the questions in the email. A fact that list could have held is how many routers, or where they ship. Iteration 2 cleared that list and did not replace it with those facts. An empty list in that situation is still a 0.

Same rule on the other empty lists from Task 6. 28763 has no purchase date and no serial, and the warranty status is not in the ticket. 28921 never names the modules or which reports HR cannot produce. 29206 names an "updated prioritization matrix" and does not say what it is. Those are 0s while the list is empty.
