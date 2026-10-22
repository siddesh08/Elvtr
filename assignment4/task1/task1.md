# Task 1 — Analyze Validation Errors

I scored the Homework 3 validation predictions. I did not open the test split. The prediction file is `assignment3/task2/outputs/validation_predictions.csv`, 3,755 rows, the same metrics as Homework 3 Task 1. A department that the model never recommends would get precision 0. That case did not come up.

1,769 tickets are correct. Accuracy is 0.471. Macro recall is 0.535. Macro F1 is 0.481.

| Department | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Billing and Payments | 380 | 0.762 | 0.742 | 0.752 |
| Customer Service | 565 | 0.399 | 0.382 | 0.391 |
| General Inquiry | 53 | 0.381 | 0.604 | 0.467 |
| Human Resources | 71 | 0.476 | 0.563 | 0.516 |
| IT Support | 449 | 0.367 | 0.430 | 0.396 |
| Product Support | 695 | 0.472 | 0.355 | 0.406 |
| Returns and Exchanges | 185 | 0.327 | 0.476 | 0.388 |
| Sales and Pre-Sales | 114 | 0.319 | 0.649 | 0.428 |
| Service Outages and Maintenance | 148 | 0.484 | 0.703 | 0.573 |
| Technical Support | 1,095 | 0.541 | 0.450 | 0.492 |

Billing is the only department I would call solid. Returns has the worst F1, then Customer Service, then IT Support. Product Support has the worst recall of the large departments, 0.355. Technical Support is the largest queue and still misses 602 of its own tickets.

Rows are the true department. Columns are the recommended department.

| True \ predicted | Billing | Cust. Svc | General | HR | IT | Product | Returns | Sales | Outages | Technical |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Billing and Payments | 282 | 31 | 0 | 3 | 11 | 6 | 13 | 14 | 1 | 19 |
| Customer Service | 20 | 216 | 12 | 8 | 50 | 75 | 37 | 41 | 12 | 94 |
| General Inquiry | 0 | 5 | 32 | 1 | 4 | 4 | 2 | 2 | 0 | 3 |
| Human Resources | 3 | 4 | 1 | 40 | 2 | 7 | 5 | 3 | 1 | 5 |
| IT Support | 7 | 46 | 7 | 5 | 193 | 36 | 15 | 17 | 18 | 105 |
| Product Support | 14 | 93 | 10 | 10 | 73 | 247 | 44 | 34 | 18 | 152 |
| Returns and Exchanges | 8 | 21 | 3 | 2 | 9 | 18 | 88 | 9 | 3 | 24 |
| Sales and Pre-Sales | 5 | 11 | 1 | 1 | 6 | 6 | 5 | 74 | 1 | 4 |
| Service Outages and Maintenance | 2 | 3 | 2 | 1 | 18 | 1 | 2 | 3 | 104 | 12 |
| Technical Support | 29 | 111 | 16 | 13 | 160 | 123 | 58 | 35 | 57 | 493 |

## The slice

The slice is a validation ticket whose true department and predicted department are two different members of Technical Support, Product Support, and IT Support.

That is 649 tickets. They are 1,986 wrong routes, about a third of the misses, and 649 / 3,755 is 17 points of accuracy sitting in one family. The median gap between the predicted probability and the true department's probability is 0.069. 241 of the 649 are under 0.05. 420 are under 0.10. The model is often unsure, and it still lands on the wrong support desk.

The six directions:

| True | Predicted | Tickets |
| --- | --- | ---: |
| Technical Support | IT Support | 160 |
| Product Support | Technical Support | 152 |
| Technical Support | Product Support | 123 |
| IT Support | Technical Support | 105 |
| Product Support | IT Support | 73 |
| IT Support | Product Support | 36 |

Technical Support's 602 misses include 283 that go to IT Support or Product Support. Product Support's 448 misses include 225 that stay inside this trio. IT Support's 256 misses include 141 that do. The same tickets are false positives on the way in. 233 of IT Support's 333 false positives came from the other two. 257 of Technical Support's 418 false positives did. 159 of Product Support's 276 false positives did. Recall and precision on these three move together.

I did not pick Returns, even though 0.388 is the lowest F1. Returns has 97 misses and the biggest single cell is 24, into Technical Support. That is a thin, scattered miss. Customer Service is the other large sink: Technical Support loses 111 tickets to it, and Product Support loses 93. I left those out. A Customer Service miss often reads like a general complaint, and the errors fan out into Sales, Returns, and Billing as well. I wanted one family where both desks are support desks and the body is the same kind of troubleshooting text.

## How I picked the 48, and how I read them

649 is too many to write up one by one. For each of the six directions I sorted by `ticket_id` and took the first 8. That is 48 tickets. The rule does not look at the text, so I did not keep the interesting ones and drop the dull ones.

The sample is balanced on purpose. IT Support to Product Support is only 36 tickets in the whole validation set, so 8 of them is a large share of that cell. Technical Support to IT Support is 160, so 8 is a small share. The category counts below are counts inside these 48. They are not the rates in the 649.

For each ticket I ran the body through the same cleaner as `TicketRouter`, then multiplied the nonzero tf-idf values by that class's logistic-regression coefficient. Those products are what I mean by a push. The probability is still the model's probability. A push is the reason I give for it. The names of products in the text are often weak next to a few common words. On the fitted model, IT Support's coefficient is 2.12 on `network`, 2.06 on `website`, 1.83 on `server`, 1.62 on `devices`, 1.61 on `marketing`, and 1.45 on `restarting`. Technical Support's coefficient on `crashes` is 2.21, and Product Support's is 2.05. `breach` is 1.12 for Technical Support. `firewall` is 1.40 for Technical Support. `campaign` is 1.16 for Product Support and negative for IT Support. `api` is 1.30 and `integration` is 1.28 for Product Support. `firmware` is 1.24 for Product Support. `Outlook` is only 0.67 for IT Support and -0.28 for Technical Support, on 57 training tickets. `PowerPoint` is about zero for all three.

## Technical Support predicted as IT Support

**54.** True Technical Support, predicted IT Support, 0.219 against 0.194.
Cue word. Outlook, calendar sync, and network equipment are all down. The biggest push is `network` at +0.233, more than twice the next term. IT Support's coefficient on that word is 2.12. The ticket never says the network team owns it rather than technical support. The margin is 0.025.

**432.** True Technical Support, predicted IT Support, 0.262 against 0.240.
Cue word. Connection failures after a firmware upgrade and a network change. `network`, `devices`, and `connection` are the three pushes, close together. Firmware does push Technical Support. It does not beat `network`.

**460.** True Technical Support, predicted IT Support, 0.244 against 0.182.
Cue word. An irrigation controller that keeps dropping off. The user already rebooted it and checked the network. `network` is the largest push, then `connection`. The irrigation setup is not a feature the model uses. The route is the word network.

**820.** True Technical Support, predicted IT Support, 0.376 against 0.153.
Cue word. One short sentence: a marketing agency cannot open the website after a software update. `website` pushes +0.472 and `the website` pushes +0.331. This is the least close call in the Technical Support to IT Support group. The body is 102 characters, so two n-grams are most of the vector.

**1134.** True Technical Support, predicted IT Support, 0.274 against 0.150.
Cue word. Campaigns are underperforming and the user suspects Oracle and the marketing tools. The pushes are `marketing` and `marketing tools`. Marketing's IT Support coefficient is 1.61. The troubleshooting in the body is real, and the word that scores is the agency, not the database.

**1158.** True Technical Support, predicted IT Support, 0.335 against 0.289.
Cue word. Digital tools at a marketing agency, maybe a software or hardware conflict, devices restarted. `digital tools` is +0.195. That phrase has an IT Support coefficient of 1.74. The true department's pushes on the same sentence are smaller.

**1227.** True Technical Support, predicted IT Support, 0.244 against 0.228.
Cue word. PowerPoint, JIRA, and Figma are down, and the user already restarted devices and reinstalled. The named products are not what scores. `digital tools` and `network` are. The gap is 0.016.

**1339.** True Technical Support, predicted IT Support, 0.347 against 0.174.
Shared wording. Scanners, antivirus, and peripherals, with a hardware/software conflict. The largest push is the bigram `and software`, then `malfunctions` and `devices`. No one word runs away with it, and the gap is still wide, 0.173, because several of those words lean IT Support together.

## IT Support predicted as Technical Support

**100.** True IT Support, predicted Technical Support, 0.252 against 0.120.
Shared wording. Smart devices and IoT apps will not sync. Reboot and firmware update already tried. The largest Technical Support push is `devices`, and that word's coefficient is actually higher for IT Support (1.62) than for Technical Support (0.69). The win is the rest of the sentence adding up. Product Support is second at 0.185, so the true desk is third.

**120.** True IT Support, predicted Technical Support, 0.304 against 0.253.
Shared wording. After an Ubuntu update, an Anker USB-C adapter, a Logitech StreamCam, and a MacBook Pro drop their connection. The largest Technical Support push is `connection`. `network` pushes IT Support by more than it pushes Technical Support, and Technical Support still wins, 0.304 to 0.253. The device names are in the vocabulary and they are not carrying the decision.

**216.** True IT Support, predicted Technical Support, 0.219 against 0.122.
Shared wording. An Intel Optane H10 stopped being recognized. The pushes are `memory`, `system`, and `device`, all modest. IT Support is not even second. Product Support is second at 0.192. The body is a single broken component and the model has no strong desk for it.

**584.** True IT Support, predicted Technical Support, 0.284 against 0.104.
Shared wording. A data analytics tool stopped taking updates after a patch. Reboot and log review failed. The top pushes are `ceased` and `has ceased`, which is the same fact twice. Nothing in the sentence is specific to Technical Support as against IT Support.

**638.** True IT Support, predicted Technical Support, 0.247 against 0.213.
Shared wording. Software and hardware went unresponsive after updates and network changes. Devices were restarted. The top Technical Support pushes are `problem` and `restarted`, almost tied. `network` contributes more to IT Support than either of those contributes to Technical Support. The probability still tips the other way, by 0.034.

**741.** True IT Support, predicted Technical Support, 0.344 against 0.203.
Shared wording. A data analytics system used for investment work, plus a guess about software conflicts or security. The largest push is `which is`. That is grammar from "which is disrupting," not the fault. `software conflicts` is next and it is small.

**1002.** True IT Support, predicted Technical Support, 0.256 against 0.207.
Cue word. A hospital security system flagged unauthorized access and the user suspects malware. `breach` is the top push, barely ahead of `hospital security`. Breach is a Technical Support word, coefficient 1.12. The ticket is four lines, so that word matters.

**1353.** True IT Support, predicted Technical Support, 0.367 against 0.152.
Cue word. Software crashes after updates, rollback and reboot already failed. `crashes` pushes +0.200. The Technical Support coefficient on it is 2.21. The true department gets a much smaller push from the same word. This one is not a close call.

## Technical Support predicted as Product Support

**56.** True Technical Support, predicted Product Support, 0.195 against 0.141.
Shared wording. A telehealth security breach, and the ask is an investigation. The winning pushes are `highlight` and `patient`, both about +0.05. `breach` actually pushes the true department. It loses to a pile of small Product Support weights. Four departments sit between 0.126 and 0.195.

**313.** True Technical Support, predicted Product Support, 0.226 against 0.220.
Cue word. A Bose headset will not stay connected to a QNAP NAS. Firmware is current, devices were restarted. `firmware` is the top push. Product Support's coefficient on it is 1.24, against 0.66 for Technical Support. The margin is 0.006. Bose and QNAP are not what decided it.

**455.** True Technical Support, predicted Product Support, 0.224 against 0.214.
Cue word. Outlook mail will not sync between a laptop and a phone. The top push is `device`. That coefficient is 0.87 for Product Support and negative for IT Support. `Outlook` itself is -0.28 for the true department. The gap is 0.010.

**583.** True Technical Support, predicted Product Support, 0.191 against 0.117.
Cue word. A marketing campaign missed, and the user thinks MySQL connectivity is involved. They checked database connections and rebooted network devices. `campaign` pushes +0.145, about twice `mysql`. The campaign coefficient is why this went to Product Support instead of staying with the database fault.

**608.** True Technical Support, predicted Product Support, 0.335 against 0.100.
Not a fault report. "I need assistance with digital marketing strategies." The work is campaign settings and audience targeting, not a broken system. `and adjusting` and `campaign` are the pushes. The label says Technical Support. The body does not describe a technical fault.

**911.** True Technical Support, predicted Product Support, 0.188 against 0.161.
Shared wording. The data analytics platform used for investment work is down, suspected software bug or corruption. Restart did not help. The top push is `efforts to`. IT Support and Service Outages are both at 0.16, level with the true label. Nobody's cue word is in the sentence.

**986.** True Technical Support, predicted Product Support, 0.175 against 0.152.
Shared wording. Unauthorized access to medical records, firewall logs already checked. `firewall` is the strongest push for the true department, about +0.096. Product Support still wins, on `to highlight` and `highlight`. The greeting is beating the only concrete clue.

**1059.** True Technical Support, predicted Product Support, 0.239 against 0.215.
Cue word. SaaS integrations failed on an API compatibility problem. Services were restarted and caches cleared. `integrations` is +0.182 and `api` is +0.114. Those coefficients sit on Product Support (1.02 and 1.30). Technical Support also has a positive `api` weight, and it is not enough.

## Product Support predicted as Technical Support

**146.** True Product Support, predicted Technical Support, 0.229 against 0.216.
Shared wording. A touchscreen stopped taking touches during a client demo, right after a system upgrade. Cables were reseated. The top pushes are `during` and `problem`. The gap is 0.013. The campaign mention does push Product Support, and it loses.

**158.** True Product Support, predicted Technical Support, 0.219 against 0.200.
Shared wording. A Chromebook keeps dropping cloud apps and the analytics dashboards. Network settings were reset. `problem` and `connection` are tied for the top push. The Chromebook is not a feature that matters here.

**180.** True Product Support, predicted Technical Support, 0.239 against 0.146.
Not a fault report. The user wants integration instructions for cleaning robots and NAS boxes in a hospital, including network specs and security practices. Nothing is broken. The top pushes are `into our` and `best`. The true department is a distant second.

**275.** True Product Support, predicted Technical Support, 0.224 against 0.204.
Shared wording. Smart-device security systems failed at once and the user suspects a cyber attack. Incident response is already running. The top push is `immediate`, then `we`. There is no product name and no error. The two probabilities are 0.02 apart.

**738.** True Product Support, predicted Technical Support, 0.198 against 0.196.
Shared wording. A project-management SaaS platform is slow after a database change. Restarting services and clearing cache helped somewhat. `database` and `platform` lead, and the gap is 0.002. This is a coin flip on ordinary ops words.

**1074.** True Product Support, predicted Technical Support, 0.222 against 0.127.
Cue word. Security flaws in hospital medical records, old software, firewall settings changed, and the text says the situation was fully resolved. `firewall` is the top push. That coefficient is 1.40 for Technical Support. The ticket is also written as a closed incident, so there is no open product fault for the model to find.

**1187.** True Product Support, predicted Technical Support, 0.246 against 0.175.
Cue word. Hospital systems, suspected breach or malware, scans and password resets already done. `breach` pushes +0.217, twice the next term. The word occurs three times. Technical Support owns that coefficient.

**1250.** True Product Support, predicted Technical Support, 0.216 against 0.149.
Cue word. Same kind of ticket as 1187. Phishing, password resets, multi-factor authentication, breach not contained. `breach` and `the breach` are the top two pushes. The hospital detail does not bring it back to Product Support.

## Product Support predicted as IT Support

**1197.** True Product Support, predicted IT Support, 0.260 against 0.106.
Not a fault report. The body is a draft request to update and integrate analytics tools for investment analysis. No failure is described. `various software` and `request for` are the pushes. Sales is the second-place department, not Product Support.

**1262.** True Product Support, predicted IT Support, 0.173 against 0.170.
Cue word. A marketing agency has product problems, and the troubleshooting list includes connectivity tests. `connectivity` is the top push. IT Support's coefficient on it is 1.53. The margin is 0.003, so the rest of the ticket almost held Product Support.

**1470.** True Product Support, predicted IT Support, 0.224 against 0.119.
Shared wording. A SaaS project tool slowed down, possibly Elasticsearch indexing. Caches cleared, services restarted. The top push is `and restarted`. Elasticsearch's coefficient is actually higher for Technical Support than for either of these two, and Technical Support came in second. The true label is third.

**1647.** True Product Support, predicted IT Support, 0.224 against 0.131.
Shared wording. Marketing campaigns stopped, suspected software conflict, devices restarted, software checked. The largest push is `our`, then `devices`. Campaigns do push Product Support. They lose to the restart-the-devices wording, which leans IT Support.

**1945.** True Product Support, predicted IT Support, 0.255 against 0.173.
Shared wording. This is 1647 with a few words swapped (`unexpectedly`, `regrettably`, a phone-number placeholder). Same route, same reason. `unexpectedly` leads this time, then `devices`. A repeated template gets the same wrong desk twice, which is what a bag of n-grams will do.

**1974.** True Product Support, predicted IT Support, 0.197 against 0.187.
Not a fault report. The user wants to revisit a digital marketing strategy and get recommendations. `our` and `it` are the top pushes. The gap is 0.011. There is no product defect in the text for the model to recover.

**2020.** True Product Support, predicted IT Support, 0.240 against 0.190.
Cue word. The report feature in a project-management SaaS tool fails to sync, and the user blames server load at peak hours. Cache cleared, services restarted. `server` pushes +0.214. IT Support's coefficient on it is 1.83. The feature that is broken is a product feature. The word that scores is server.

**2275.** True Product Support, predicted IT Support, 0.184 against 0.137.
Not a fault report. A request for guidance on securing Cassandra, Oracle, and the hospital network. Patches and best practices, not an outage. `network` is the top push, coefficient 2.12 on IT Support. Sales is second. The true department is third.

## IT Support predicted as Product Support

**141.** True IT Support, predicted Product Support, 0.172 against 0.144.
Shared wording. PowerPoint 2021 collaborative editing loses edits. The top push is `screen`, then `when`. PowerPoint's coefficient is about zero, slightly negative, for all three support departments. The product name is in the sentence and it does not vote.

**494.** True IT Support, predicted Product Support, 0.237 against 0.190.
Cue word. The computer stopped seeing USB drives. Reboot, driver update, Device Manager. The top push is `device`, and that coefficient is positive for Product Support and negative for IT Support. `computer` and `drivers` push the true department and lose on the sum.

**1421.** True IT Support, predicted Product Support, 0.283 against 0.088.
Shared wording. A finance shop is slow processing data, maybe an overloaded server. Servers were rebooted and caches cleared. The top pushes are `efforts to` and `encountered delays`. `server` pushes IT Support hard and the ticket still goes to Product Support by a wide margin, 0.195. The true desk is fourth.

**2410.** True IT Support, predicted Product Support, 0.312 against 0.118.
Shared wording. Products show sync errors after an update. The user restarted apps, cleared caches, and reinstalled. `caches and` leads, `integrations` is second. Both lean Product Support. The steps are the generic playbook, and the gap is wide.

**2471.** True IT Support, predicted Product Support, 0.213 against 0.147.
Not a fault report. "Can you provide assistance with effectively integrating CorelDRAW." The user wants to use it in a marketing workflow. `content and` and `and streamline` are the pushes. CorelDRAW's own coefficient is small and points at IT Support, the true label, and it is not enough to beat the how-to wording.

**4225.** True IT Support, predicted Product Support, 0.256 against 0.067.
Not a fault report. The digital marketing approach is not growing the brand. The ask is to rethink content, SEO, and targeting. `strategy` is the top push. IT Support is not in the top four probabilities. Human Resources is second.

**5055.** True IT Support, predicted Product Support, 0.175 against 0.165.
Not a fault report. A request for best practices on protecting patient data with Firebase and Kaspersky. `patient` and `patient data` are the pushes. The gap is 0.011. Firebase's coefficient does point at IT Support. The patient wording outweighs it.

**5260.** True IT Support, predicted Product Support, 0.193 against 0.155.
Shared wording. Sporadic delays on a SaaS platform, blamed on server overload. Cache cleared, server restarted. The top push is `sporadic`, then `and`. `server` is the strongest push for the true department. Technical Support is second. The platform and the server are both in the text, and the model follows the vaguer words.

## The three categories

**Shared wording.** 21 of the 48. The ticket is a real fault, or a security incident told in the same flat way. The pushes are words all three departments use, or they are small enough that no one of them is the decision: restart, software, device, problem, connection, update, and a few boilerplate bits like `highlight` and `which is`. The probabilities are usually close. The 21 are: 56, 100, 120, 141, 146, 158, 216, 275, 584, 638, 738, 741, 911, 986, 1339, 1421, 1470, 1647, 1945, 2410, 5260.

This is the category that matches the full slice. Most of those 649 are close. It hits recall on all three departments, and it hits precision too, because one department's miss is another's extra ticket. IT Support's precision is 0.367 largely because of tickets like these.

A cleaner change does not fix it. The Homework 2 cleaner already ran inside `fit` and `predict`, and the words that score are ordinary English, not `<br>` tags or glued punctuation. Some of it is addressable with a model change, and only where the body also names a specific system. Those names are already in the vocabulary. Their coefficients are too small, or they point at the wrong desk, so `network` and `devices` outvote them. Where the body never names anything that belongs to one department, I do not see a feature change that creates the missing fact.

**Cue word.** 19 of the 48. The ticket is also usually a fault, and one n-gram with a large coefficient on the predicted department is the biggest push. The ids are 54, 313, 432, 455, 460, 494, 583, 820, 1002, 1059, 1074, 1134, 1158, 1187, 1227, 1250, 1262, 1353, 2020.

The repeated ones are `network`, `website`, `server`, `crashes`, `breach`, `firewall`, `campaign`, `marketing`, `api`, `integrations`, `digital tools`, `firmware`, `connectivity`, and `device`. Ticket 820 is the plain version: a 102-character body, `website` at +0.472, IT Support at 0.376 against Technical Support at 0.153. Tickets 1187 and 1250 are the same version for `breach`. Ticket 2020 is a broken product feature that loses on the word `server`.

This one is addressable with a model change. The mechanism is the weight, not a character the cleaner missed. I would not strip `network` or `server` out of the text. Those words are legitimate in the department that owns them, and deleting them would throw away real IT Support tickets. The lever is that the weight is large enough to ignore the rest of the body, including the product name.

This is the category I would take into a later change. I can point at the coefficient. Shared wording is real, and a change aimed at it has nowhere to hold on when the ticket is only generic verbs.

**Not a fault report.** 8 of the 48. The ids are 180, 608, 1197, 1974, 2275, 2471, 4225, 5055.

These ask for a how-to, a strategy review, campaign results, or best practices. 608 is digital marketing strategy. 2471 is how to integrate CorelDRAW. 4225 is a marketing plan that is not growing the brand, and IT Support is not even in the top four. 2275 asks how to secure Cassandra and Oracle, and `network` happens to be in the sentence, so IT Support wins a request that is not an IT failure.

I do not see a model or preprocessing change that fixes these without fighting the text. The label is one of the three support departments. The body is a different kind of request. Relabeling is not available. Training harder on the given label would teach the router that a strategy question belongs on a break/fix desk.

## What I would carry forward

The consequential pattern is the 649 tickets these three departments trade. Inside the 48 I read, the part I can actually aim at is the cue-word group: a small set of high coefficients overriding the system named in the ticket. Shared wording is the larger group and the reason the probabilities are so close, and a lot of it will remain after any one change. The eight non-fault tickets should stay wrong under the current labels.
