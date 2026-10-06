# Task 1 — Clean the Data

**Source file (not modified):** `assignment2/homework_materials/SIDDESH NATESAN - support_tickets - SIDDESH NATESAN - support_tickets.csv`

**Cleaned file:** `assignment2/task1/outputs/cleaned_support_tickets.csv`

**Environment:** `.venv` with `assignment2/homework_materials/requirements.txt` (`pandas==3.0.5`, `scikit-learn==1.9.1`, `joblib==1.6.0`). This task only imports `pandas`. The other two packages are pinned for the later tasks.

**How to re-run** (from the repository root):

```bash
.venv/bin/pip install -r assignment2/homework_materials/requirements.txt
.venv/bin/python assignment2/task1/clean_tickets.py
```

The script reads the canonical CSV, cleans `Body` only, and writes the cleaned CSV. It checks that the row count is still 29,651, that `ticket_id` is unchanged and unique, and that `Department`, `Priority`, and `Tags` are copied through. A second pass over the cleaned text does not change it again.

I did not use a text-cleaning library. The edits are `str.translate`, `str.replace`, and a few regular expressions in `clean_tickets.py`. The dataset card already gives the schema and the label counts, so I did not redo that profile. I looked for record-level problems in `Body` and decided which ones to edit.

2,639 bodies actually change. The counts below overlap, so they add up to more than 2,639. A ticket can have a `<br>` and also a missing space.

`Department`, `Priority`, and `Tags` are not rewritten. Lowercasing and class imbalance belong in preprocessing (Task 3), not here.

---

## 1. HTML line breaks, and two broken versions of the same thing

**What the issue was.** Some bodies contain line-break markup instead of a space or a newline. There are no real newline characters in the file.

- 652 records have `<br>`, `<br/>`, or `<br />`. Example: ticket `630` starts `Dear Customer Support,<br><br>I am submitting a report...`. Ticket `16331` uses the spaced form `<br />`.
- 18 records lost the brackets and contain the letters `brbr`. Example: ticket `28321` is `Hello,brbrI am experiencing frequent crashes...`. Also `28425`, `28471`, `28568`.
- 1 record, ticket `19862`, has a normal `<br><br>` and also `<brWarm regards`, where the `>` after `br` was never written.

That is 670 records. Ticket `19862` is inside the 652 and is also the broken-tag case.

**Why I consider it an issue.** `<br>` and `brbr` are not words the customer wrote. If they stay in the text, the later vectorizer can treat them as features. They show up in several departments, so they are not a useful routing signal. They also glue the next sentence to the greeting (`<br><br>I`).

**How I addressed it.** Replace `<br>`, `<br/>`, and `<br />` with a space. Replace a `<br` that is immediately followed by a letter (the `19862` case) with a space. Replace the literal `brbr` with a space. A later step collapses the extra spaces this leaves behind.

**How many records.** 670, as counted above.

**Representative ticket ids.** `630`, `633`, `795`, `16331`, `28321`, `28425`, `19862`.

**Risk or limitation.** If a ticket were discussing the HTML tag itself, that mention would be removed. I did not see that use. This pattern does not match the redaction placeholders (`<tel_num>`, `<name>`, `<acc_num>`, and similar), so those stay.

---

## 2. Missing space when the next letter is a capital

**What the issue was.** Punctuation is often stuck to the next word when that word starts with a capital letter. Ticket `1` reads `Dear Customer Support Team,I am writing to report...` and later `persists.Could you please`. The same pattern is on tickets `2` through `5` and many others. The common pairs are `,I`, `.T` (as in `.Thank` / `.The`), and `.B` (as in `.Best`).

**Why I consider it an issue.** `Team,I` is one token until something splits it. The greeting and the first sentence of the request get fused, and so do sentence boundaries further down (`persists.Could`). That is a formatting error from how the text was exported, not part of the customer's wording.

**How I addressed it.** If `,`, `.`, `:`, `;`, `!`, or `?` is immediately followed by `A`–`Z`, insert one space. I only do this for a capital letter.

**How many records.** 1,924.

**Representative ticket ids.** `1`, `2`, `3`, `630`, `28296`.

**Risk or limitation.** An abbreviation with a capital after the period would be split (`Ph.D` would become `Ph. D`). I did not apply the same rule to a lowercase letter, because that would break real tokens. Ticket `739` contains `Node.js`, and `.js` appears in 199 bodies. Those are unchanged. The same is true of `.com` and `.ai` glued to a lowercase word.

---

## 3. Curly apostrophes

**What the issue was.** 71 bodies use a curly apostrophe (`’` or `‘`) instead of `'`. Ticket `28296` has this in `store’s policy`. All 71 are in ticket ids `28296` through `29649`, so they look like one export batch rather than customer spelling.

**Why I consider it an issue.** `store’s` and `store's` are the same word. Leaving both forms in would split one word into two vocabulary entries later.

**How I addressed it.** Map `‘` and `’` to `'`. I also mapped `“` and `”` to `"` in the same table. The file does not actually contain the curly double quotes. I left `ü`, `ä`, and `ö` alone (see below).

**How many records.** 71.

**Representative ticket ids.** `28296`, `28305`, `28309`, `28333`, `28338`.

**Risk or limitation.** A curly apostrophe that was meant as a distinct character would be flattened. In this file it is only the ordinary possessive or contraction mark.

---

## 4. Extra whitespace, including one non-breaking space

**What the issue was.** 45 bodies already have messy spacing before any other edit:

- Leading or trailing whitespace: 23 records. Ticket `2047` has trailing space.
- Runs of more than one space: 25 records. Ticket `6805` has long gaps around a `<br>` (`<br>            Reporting`).
- A non-breaking space (`U+00A0`): ticket `29291`, in `acc_num. Your` where the space is not a normal space.

Those three counts overlap, which is why the union is 45 rather than 49.

**Why I consider it an issue.** Leading and trailing space changes the string without adding words. A non-breaking space does not match a normal space, so the same sentence would not compare equal. Repeated spaces are layout from the `<br>` lines, not part of the request.

**How I addressed it.** The non-breaking space becomes a normal space in the same character map as the curly apostrophes. After the other edits, any run of whitespace is collapsed to a single space and the ends are stripped. This last pass also cleans spaces that the line-break removal just created, so it touches 592 bodies in total. Only 45 of those were already messy in the raw file. I am counting 45 as the records with this issue.

**Representative ticket ids.** `2047`, `2262`, `6805`, `9097`, `29291`.

**Risk or limitation.** Collapsing whitespace would hurt text where the spacing itself carried meaning (aligned columns, for example). These bodies are prose. I did not try to restore paragraph breaks, because the source has no newline characters to recover. A `<br><br>` becomes one space, not a blank line.

---

## 5. The one missing body

**What the issue was.** Ticket `28902` has no `Body`. `Department` is Product Support, `Priority` is high, and `Tags` is filled in. The dataset card already reports this single missing body. Nothing else is missing in `ticket_id`, `Department`, `Priority`, or `Tags`.

**Why I consider it an issue.** There is no request text to route on. A model cannot use this row as a text example.

**How I addressed it.** I kept the row and left `Body` as an empty string. I did not invent text, and I did not drop the row. Dropping it would remove `ticket_id` `28902`. The cleaned file still has ticket ids `1` through `29651`, each once.

**How many records.** 1.

**Representative ticket id.** `28902`.

**Risk or limitation.** The empty string is not useful training text. If a later step feeds every row to the model without skipping blanks, this one labeled row contributes an empty feature vector. I would skip it when building the matrices in Task 3, but the row stays in the cleaned table so the id is not lost.

---

## Issues I left alone

These are real, but changing them here would throw away information or would guess at the label.

### Redaction placeholders

**Issue.** 356 bodies contain tags like `<tel_num>`, `<acc_num>`, `<name>`, `<email>`, `<ref_num>`, `<website_url>`, or `<user>`. Ticket `963` says `Our contact number is <tel_num>.` A few sign-offs also have glued fake addresses (`name@example.com`, sometimes run into `tel`). I counted 33 bodies with an `@` that looks like an email. They are placeholders, not live customer addresses.

**Why it matters.** The original publisher already stripped phone numbers, account numbers, and names. The tag is the residue.

**What I did.** Nothing. Ticket `963` is byte-for-byte the same in the cleaned file.

**Risk of removing them.** Deleting `<tel_num>` often leaves a hole in the sentence, and a sloppy email regex grabs the surrounding redaction (`namename@company.comtel`). The tag also tells me a phone number used to be there, which is weakly related to account and billing tickets. I would rather keep that token than guess a replacement.

### German characters in product names

**Issue.** 82 bodies contain `ü`, `ä`, or `ö`. Ticket `33` asks about integrating the `Smart-Türklingel` video doorbell. Also `38`, `272`, `371`, `799`. None of these 82 are the curly-apostrophe records, and none of them is the non-breaking space.

**Why it matters.** The character is part of the product name. It is not mojibake. The text is already NFC, so there is no decomposed-accent duplicate to fold.

**What I did.** Left the letters in place. Ticket `33` still contains `Türklingel` after cleaning. That ticket did change, but only because of the missing space in `Team,I`.

**Risk of stripping them.** Replacing `ü` with `u` would make `Türklingel` and a hypothetical `Turklingel` the same word and would hide the product. There is no gain for routing.

### Punctuation glued to a lowercase letter

**Issue.** 1,324 bodies have punctuation immediately followed by a lowercase letter. A lot of this is `Node.js`, `.com`, or `.ai`. Another chunk is the redaction glue `,name` / `,nameacc` in the sign-off, as on ticket `28262` (`Best regards,nameacc_num`).

**Why it matters.** Some of these are real missing spaces. Many are not.

**What I did.** Deferred. The capital-letter rule above covers the clear sentence breaks. A blanket lowercase rule would turn `Node.js` into `Node. js` on ticket `739`.

**Risk of the choice I made.** `Best regards,name` stays glued. That is ugly, but it is the publisher's placeholder, and splitting only the `,name` cases would be a special case on top of a special case. The routing words are earlier in the body.

### Repeated bodies

**Issue.** 9,190 rows share their exact `Body` with at least one other row. That is 4,594 repeated texts, up to 4 copies. Almost all of those copies have the same `Department`. 9 texts do not: 20 rows. The clearest one is `Assistance Required`, labeled Product Support (`5928`), Billing and Payments (`9070` and `21596`), and Technical Support (`19516`). Other conflicting texts are just as short: `Seeking assistance` (`2761`, `17244`), `Seeking information` (`11054`, `24872`).

**Why it matters.** Exact copies can land in both train and test later and make a model look better than it is. The 9 conflicts also mean the same words have more than one official label.

**What I did.** Kept every copy. I am not going to pick a department for `Assistance Required`. The text is too thin to decide, and deleting rows would drop ticket ids. The split in Task 2 should put identical bodies in the same partition. I am leaving that to the split on purpose.

**Risk of keeping them.** If the split ignores duplicates, evaluation in Homework 3 will be optimistic. That is a split problem, not something to solve by deleting text now.

### Very short bodies

**Issue.** 330 bodies are 1 to 40 characters and are not the empty ticket. Ticket `707` is `Our system` (Technical Support). Ticket `554` is `Requesting Assistance` (Product Support). Ticket `996` is `Assistance Needed` (Technical Support).

**Why it matters.** There is almost no content to classify. Several of the label conflicts above are in this group.

**What I did.** Kept them. A short ticket is still a ticket that was routed.

**Risk of keeping them.** They will be easy to memorize and hard to route for the right reason. Filtering them out would drop terse requests and would change the label mix. I can revisit that when I look at errors, not during cleaning.

### Case, labels, and the other columns

I did not lowercase `Body`. Product names and short forms (`IT`, `API`, `SQL`) are still capitalized. Task 3 is where the vectorizer gets to decide case.

I did not resample departments. Technical Support has 8,617 rows and General Inquiry has 419. That imbalance is a modeling choice in Task 3, and the dataset card already states it.

`Priority` is only `low`, `medium`, and `high`. `Tags` is a serialized list. Neither field is the ticket text the classifier is supposed to read, and neither has missing values. I copied both columns unchanged.
