# Task 3 — Prepare the Vector-Store Records

The script is `prepare_records.py`. The records are `records.json`. I did not embed anything, and I did not call `VectorStore`.

Re-run from the repository root:

```bash
.venv/bin/python assignment5/task3/prepare_records.py
```

The run is deterministic. A second run writes the same file. 32 articles become 134 chunks. The shortest chunk is 110 characters. The longest is 954.

## How a chunk is cut

Each article is a frontmatter block and then `##` sections. I take one chunk per section, in the order the headings appear. The chunk `content` is the file text from that heading up to, and not including, the next heading. I do not rewrap lines or drop the heading. The frontmatter is not a chunk. `article_id` and `title` move into metadata, and the rest of the frontmatter stays out.

`chunk_id` is the article id, a hyphen, and the section index as two digits. The first section is `00`. `KB-JIRA-NEG-001-03` is the Limits section of the Jira notification article. The ids are unique. They stay put for this corpus because the supplied articles are `hw5_kb_v1` and I number sections in file order. I read the files in filename order so the JSON list does not depend on directory order.

I did not use a character window. The sections are already the units the articles were written in. The Canon head-cleaning steps are one section. The maintenance window, with the date and the two 10-minute interruptions, is one section. A fixed window would cut those in half, and the size I picked would be arbitrary.

I did not embed a whole article either. The longest body is 2,540 characters, on the AWS billing-review article. `bge-small-en-v1.5` takes 512 tokens. I did not tokenize the files. A body that long is close enough to the cap that the last section can fall off, and the last section is often Limits, which is the part that says what the article does not cover. The longest section I kept is 954 characters, so the passage fits.

Most articles have four sections. The range is three to five. Splitting again, into paragraphs, would mostly duplicate "What the customer provides" and "What support provides". Those headings already occur on 26 and 29 articles.

## What gets embedded

`content` is the section. `embedding_text` is the article title, a blank line, then that same section. The title is not repeated inside every section, and the headings are shared. The Limits chunk of `KB-JIRA-NEG-001` is the whole point:

```
## Limits

This article does not add custom priorities, create new statuses, or define
transition conditions.
```

Embedded alone, that passage does not say Jira, and it does not say notifications. With the title in front, the passage is "Notification Schemes and Watchers in Jira Software 8.20" plus that section. The text returned after a search is still only the section.

I did not put an instruction sentence on `embedding_text`. `VectorStore.build` embeds that field as the passage. `query` embeds the ticket with `query_embed`. The passage should be the article text.

I also left the frontmatter `product` value off the passage. On the Canon, Cisco, Samsung, and Jira articles the title already names the product. On other articles `product` is a queue name, such as "Fulfillment Support" or "Account Support", and I do not want that string pulling a chunk toward a ticket that only says "support".

## Metadata

Each record has `article_id`, `title`, `chunk_position`, and `section`. The first three are the ones the task asks for. `section` is the heading with the `##` removed, because position `03` does not say Limits. `chunk_position` is an integer starting at 0, matching the index in the chunk id.
