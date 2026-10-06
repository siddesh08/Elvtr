# Task 3 — Implement Preprocessing

**Inputs (not modified):**

- `assignment2/task1/outputs/cleaned_support_tickets.csv`
- `assignment2/task2/outputs/split_manifest.csv`

**Environment:** `.venv` with `assignment2/homework_materials/requirements.txt` (`pandas==3.0.5`, `scikit-learn==1.9.1`, `joblib==1.6.0`). The vectorizer is scikit-learn's `TfidfVectorizer`. Task 1 did the cleaning without a text-cleaning library. This task is where a pre-built text utility is allowed.

**How to re-run** (from the repository root):

```bash
.venv/bin/pip install -r assignment2/homework_materials/requirements.txt
.venv/bin/python assignment2/task3/preprocess.py
```

The script joins the cleaned tickets to the manifest on `ticket_id`, builds the three splits, fits the vectorizer on the training bodies, and transforms validation and test with that same vocabulary. It writes:

- `assignment2/task3/outputs/train_vectors.npz`, `validation_vectors.npz`, `test_vectors.npz`
- `assignment2/task3/outputs/train_index.csv`, `validation_index.csv`, `test_index.csv` (same row order as the matrices; columns `ticket_id`, `Department`)
- `assignment2/task3/outputs/vectorizer.joblib`
- `assignment2/task3/outputs/class_weights.csv`

---

## Input fields

The only text I vectorize is `Body`. That is the request a new ticket arrives with, and it is the field Task 4 is supposed to classify from. `Department` is the label, so it does not go into the vector.

I left `Priority` and `Tags` out. The dataset card says the file does not document when either field was created. If they are filled in after someone has already decided the department, using them is leakage. `Tags` is also a free-form list, and on 843 tickets the tag string contains the department name itself.

Leaving `Priority` out has a cost. It is not independent of the label. Technical Support is 5,034 high out of 8,617, and Service Outages and Maintenance is 818 high out of 1,157. General Inquiry is 66 high and 246 low out of 419. Human Resources is 59 high and 271 low out of 568. If priority is actually known when the ticket arrives, a Body-only model is ignoring a useful field. I would rather ignore it than treat an after-the-fact label as an input.

Ticket `28902` has an empty `Body`. It is in the training split. I drop that one row before building vectors. There is no other empty body. The training matrix has 23,720 rows, which is the 23,721 training tickets from Task 2 minus this one. Validation stays 2,968 and test stays 2,962.

---

## Preprocessing

I use word TF-IDF, unigrams and bigrams, fit on the training bodies only.

TF-IDF downweights a word that shows up in every department, which is what I want for routing. A raw count would treat "team" the same as "outage" if both appear once in a ticket. The bigram range keeps a product name together: `Smart-Türklingel` becomes `smart`, `türklingel`, and `smart türklingel`. Lowercasing is on. I did not lowercase in Task 1 because that is a modeling choice, not a data repair. The `ü` stays, so ticket `33` does not lose the product name.

I do not remove English stop words. `not` and `no` are the difference between a product that works and one that does not, and scikit-learn's English list drops those.

`min_df=2` means a token must appear in at least two training tickets before it gets a column. A one-off typo does not become a feature. `max_df=0.95` drops a token that is in more than 95% of training tickets, because that token cannot separate departments. The fitted vocabulary has 66,275 columns. Validation and test use that vocabulary and no other: a word that appears only in the test set is ignored, which is what I want. I do not refit on validation or test.

The matrices are sparse. Training is 23,720 by 66,275 with 2,318,770 nonzero entries. Validation is 2,968 by 66,275. Test is 2,962 by 66,275. Row order inside each matrix is `ticket_id` order, and the index CSV for that split lists the same rows.

The limitation of `min_df=2` is a product or error string that really does occur once in training and once in test. Both occurrences are dropped, so the model cannot use that phrase. I would rather drop the one-off tokens than carry a column that only one training ticket supports.

Placeholder tags from Task 1 stay useful. `<tel_num>` is tokenized as `tel_num`, because the angle brackets are not word characters. I am not stripping those.

---

## Class imbalance

The imbalance is real, and it survived the split. In the training rows I actually vectorize:

| Department | Train rows | Weight |
| --- | ---: | ---: |
| Billing and Payments | 2,414 | 0.983 |
| Customer Service | 3,585 | 0.662 |
| General Inquiry | 335 | 7.081 |
| Human Resources | 454 | 5.225 |
| IT Support | 2,800 | 0.847 |
| Product Support | 4,432 | 0.535 |
| Returns and Exchanges | 1,172 | 2.024 |
| Sales and Pre-Sales | 708 | 3.350 |
| Service Outages and Maintenance | 926 | 2.562 |
| Technical Support | 6,894 | 0.344 |

Technical Support has about 20 times as many training rows as General Inquiry. A model can look accurate by leaning on the large departments and still miss the small ones. All 10 departments are real routing targets, so I am not folding the small ones into an "other" class.

I am not copying rare rows and I am not throwing away Technical Support rows. A lot of bodies are already repeated, and several of the rare texts are the short ones whose copies do not even agree on a department (`Assistance Required` and the other eight from Task 2). Copying those again would teach the model the same thin sentence more often. Cutting Technical Support would throw away wording that is not just a duplicate. I am also not generating extra tickets. Synthetic text would not fix a bad label, and the small classes are where the labels are already the least trustworthy.

What I change is the cost of a training mistake. For each department the weight is

`training rows / (10 * rows in that department)`

which is the usual balanced class weight. General Inquiry is about 7.08. Technical Support is about 0.34. Every training ticket stays in the matrix once. Validation and test are not reweighted and not resampled, so a later score still reflects the department mix from the split. The weights are in `class_weights.csv`. Task 4 can pass them into the classifier. They do not change the feature vectors.

The risk is that a large weight amplifies a noisy small class. General Inquiry's 335 training rows include very short texts. A miss on one of those now counts about 20 times a miss on a Technical Support ticket, and some of those short labels may be wrong. I do not have a real cost for "sent to the wrong team," so this weight is a frequency correction, not a business cost. If the small-class labels look bad once I can see errors, I would rather fix the labels than push the weight higher.
