# Task 1 — Select Classification Metrics

I chose these metrics before looking at any validation prediction. The only thing I checked is the label mix on the official manifest, because that mix is what makes accuracy a bad thing to steer on by itself.

The manifest keeps 25,034 of the 29,651 source tickets. The other 4,617 ids are left out. Of the tickets that remain, 17,524 are train, 3,755 are validation, and 3,755 are test. This choice, and the scoring later, uses train and validation only.

| Department | Train | Validation | Test |
| --- | ---: | ---: | ---: |
| Billing and Payments | 1,770 | 380 | 380 |
| Customer Service | 2,636 | 565 | 565 |
| General Inquiry | 249 | 53 | 53 |
| Human Resources | 332 | 71 | 71 |
| IT Support | 2,095 | 449 | 449 |
| Product Support | 3,244 | 695 | 695 |
| Returns and Exchanges | 864 | 185 | 185 |
| Sales and Pre-Sales | 531 | 114 | 114 |
| Service Outages and Maintenance | 690 | 148 | 148 |
| Technical Support | 5,113 | 1,095 | 1,095 |

Technical Support is still about 20 times General Inquiry: 5,113 against 249 in train, and 1,095 against 53 in validation. The three largest validation departments, Technical Support, Product Support, and Customer Service, are 2,355 of the 3,755 validation tickets, about 63%. A router that called every validation ticket Technical Support would already be right on 1,095 of them, about 29%, without reading the body.

The balanced class weights from Homework 2 stay inside the fit. Each validation ticket counts once when I score. A General Inquiry miss does not get counted seven times in the metric just because it counted more during training.

Each ticket is sent to one department. I score `recommended_department` against `Department`. I am leaving `class_scores` out of this set. Those scores would matter if a low score handed the ticket to a person, and I do not have that rule. A close second-place department is still a wrong route.

## What I will compute

Across the ten departments:

- Accuracy
- Macro-averaged recall
- Macro-averaged F1

For each department, treating that department as the positive class and the other nine as negative:

- Precision
- Recall
- F1

For a department `c` on the validation tickets:

- A true positive is a ticket labeled `c` and recommended `c`.
- A false positive is a ticket recommended `c` whose label is some other department.
- A false negative is a ticket labeled `c` that was sent somewhere else.

Precision for `c` is true positives divided by true positives plus false positives. That is the share of the queue that actually belongs there. If the model never recommends `c`, the denominator is zero. I will write precision as 0 in that case. A department that receives nothing is a failed route, and a blank would drop it out of the macro average.

Recall for `c` is true positives divided by true positives plus false negatives. That is the share of `c`'s own tickets that reached `c`. Every department appears in this validation split. The smallest is General Inquiry with 53 tickets, so this denominator is not zero.

F1 for `c` is `2 * precision * recall / (precision + recall)`. If precision and recall are both 0, F1 is 0.

Macro recall is the arithmetic mean of the ten recalls. Macro F1 is the arithmetic mean of the ten F1 scores. Each department has weight 1. I am not weighting those means by ticket count, and I am not computing F1 from the averaged precision and the averaged recall.

Accuracy is the number of validation tickets whose recommendation matches the label, divided by 3,755. On a single-label problem this is the same number as micro-averaged precision, micro-averaged recall, and micro-averaged F1. I am reporting it once, as accuracy.

I am not also reporting a support-weighted F1. That would be a second average pulled around by Technical Support, Product Support, and Customer Service. Accuracy already answers the volume question: what share of tickets reached the right team.

## Accuracy

**What it is.** Correct validation tickets divided by all 3,755 validation tickets. One ticket, one vote, whatever department it belongs to.

**Why it fits.** This is the share of the queue that lands on the right desk. Most of the tickets are in a few departments. If I only watch an unweighted mean, a fix on General Inquiry's 53 tickets can look as large as a fix on Technical Support's 1,095, and the second one is most of the work.

**What it hides.** The 29% that comes from always answering Technical Support, and the 63% sitting in the three largest departments. Human Resources and General Inquiry together are 124 validation tickets. Missing both of them costs about 3 points of accuracy, which is easy to overlook next to a move on Technical Support. Accuracy also treats every wrong desk as the same mistake. A billing ticket sent to Sales and an outage ticket sent to Human Resources both count as one miss. I do not have a real cost for those, so I am not going to invent weights and fold them into this number.

## Macro-averaged recall

**What it is.** Add the ten per-department recalls and divide by 10. General Inquiry's recall is one tenth of the result, same as Technical Support's.

**Why it fits.** Homework 2 kept all ten departments as real destinations instead of folding the small ones into an "other" class. Recall is the number that goes to zero when a department's tickets never arrive. The unweighted mean is what stops Technical Support's 1,095 tickets from burying General Inquiry's 53.

**What it hides.** Precision. Recommending General Inquiry on more tickets raises that department's recall even when a lot of those tickets belong somewhere else, and the macro number rises with it. The small support also makes the mean jumpy. General Inquiry has 53 validation tickets, so a few short bodies with a shaky label move its recall by several points, and that move is a full tenth of the macro recall. The same few mistakes inside Technical Support barely show up.

## Macro-averaged F1

**What it is.** Add the ten per-department F1 scores and divide by 10. Same equal weight as macro recall. A department with precision 0 and recall 0 contributes 0, not a blank.

**Why it fits.** F1 falls when a department's own tickets do not arrive, and it also falls when that department's queue fills up with other departments' tickets. Macro recall only catches the first of those. The equal weight means a higher score has to come from the departments, not from being right on Technical Support alone. That is the same reason the fit used balanced class weights. The weights changed training. This average is how I will read the validation routes.

**What it hides.** Which side failed. Precision 0.4 with recall 0.9 and precision 0.9 with recall 0.4 can land on a similar F1, and those are different problems. One queue is flooded. The other is missing its own tickets. That is why precision and recall stay in the report next to F1. Macro F1 also hides volume. Nine departments at F1 1.0 and Technical Support at F1 0.5 still average 0.95, while a large share of the tickets are on the wrong desk. And the small classes are a thin sample. A few bad labels in General Inquiry move the macro F1 as much as a few bad labels in Technical Support, even though the Technical Support estimate is much more stable.

## Per-class precision

**What it is.** For one department, true positives divided by everything the model sent to that department. With the zero rule above, a department that is never recommended scores 0.

**Why it fits.** This is the view from the team that received the ticket. If Billing and Payments is precise, most of what that queue opens is actually billing. A low precision means the team is working another department's tickets.

**What it hides.** The tickets that never arrived. A department can look precise on a small handful of tickets it did receive and still have missed most of its own queue. Precision is also unstable when the predicted count is small. I would still rather see a 0 for a department the model never uses than drop the department out of the table.

## Per-class recall

**What it is.** For one department, true positives divided by every validation ticket labeled with that department.

**Why it fits.** This is the view from the ticket's own department. Low recall on Service Outages and Maintenance means outage tickets are sitting in some other queue. Low recall on Technical Support means a lot of tickets, not just a bad average.

**What it hides.** False positives. High recall with low precision is a department that catches its tickets by taking on everybody else's. The support count matters when I read the percentage. About 50 of 53 on General Inquiry and about 1,033 of 1,095 on Technical Support are both near 94% recall, and the second figure is the one I would trust more.

## Per-class F1

**What it is.** The harmonic mean of that department's precision and recall, using the same formula as above. One number per department.

**Why it fits.** This is the list I will sort when I say which departments came out well and which came out badly. The macro F1 is only the average of this list. Precision and recall then say whether a bad F1 is a flooded queue, a missed queue, or both.

**What it hides.** The same trade that macro F1 hides, inside one department. It also has no memory of how many tickets that department represents, so the lowest F1 can be a 53-ticket class and the highest can be a 1,095-ticket class. I will read each F1 next to its validation count.

## Primary and secondary

**Primary metric: macro-averaged F1.**

This is the number I will use to compare a later model with this one. All ten departments are real queues, and the counts differ by about 20 times. Accuracy can pick up a few points from a change that only touches Technical Support, and it barely moves if the model never predicts Human Resources or General Inquiry. Macro recall would catch an abandoned department, and it would also reward over-routing into the small ones. Macro F1 falls in both of those cases: the department's tickets did not arrive, or the queue is full of tickets that belong elsewhere.

**Secondary metric: accuracy.**

Macro F1 gives Technical Support the same vote as General Inquiry. The validation set does not. 1,095 of the 3,755 validation tickets are Technical Support. If a later change lifts macro F1 and accuracy drops, the new model is better on the average department and worse on the tickets people actually file. I want that pair written down, not averaged into one score.

Per-class precision and recall are how I explain a bad F1. Macro recall is the check that the F1 is not just a precision story. I will compute all of them. I will not tune toward them ahead of macro F1, with accuracy as the volume check beside it.
