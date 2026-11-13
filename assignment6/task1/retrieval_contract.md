# Retrieval service contract

`RetrievalService.retrieve_evidence` embeds one unaltered ticket body and returns the ordered chunks from the Homework 5 vector store.

The store and the retrieval count are fixed in `__init__` and reused. The count is 5. Homework 5 measured precision 0.520 at k = 5 and 0.360 at k = 10, and the evaluation said not to raise k to buy recall. The count is not a request field, and the service does not rebuild the index per call.

The text sent to the embedder is the request `ticket_body` with no cleaning and no added title.

## Request

`retrieve_evidence` accepts one dictionary.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `ticket_body` | string | yes | The ticket `Body`, unchanged. Must contain at least one non-whitespace character. A Boolean, a number, or `null` is not a string. |

Other fields are ignored. `top_k` in the request does not change the stored count.

```json
{
  "ticket_body": "The invoice for account 4412 does not match last month."
}
```

## Response

A successful call returns one dictionary with exactly one field.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `evidence` | array | yes | Length 5. Order is rank 1 through 5, which is the order `VectorStore.query` returned. |

Each element is one object with exactly these fields:

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `rank` | integer | yes | `1` through `5`, once each, in order. A Boolean is not an integer. |
| `chunk_id` | string | yes | Non-empty. The id stored on that chunk. |
| `distance` | number | yes | One finite cosine distance from the store. |
| `content` | string | yes | The chunk's stored `content`, unchanged. |
| `metadata` | object | yes | The stored metadata object. It contains `article_id` (string), `title` (string), `chunk_position` (integer), and `section` (string). |

```json
{
  "evidence": [
    {
      "rank": 1,
      "chunk_id": "KB-AWS-BILL-002-00",
      "distance": 0.31,
      "content": "## Overview\n\n...",
      "metadata": {
        "article_id": "KB-AWS-BILL-002",
        "title": "AWS Management Service Adjustment and Discount Eligibility",
        "chunk_position": 0,
        "section": "Overview"
      }
    }
  ]
}
```

The object above shows the element shape. A real response has five elements, and `content` is the full stored section.

## Errors

The method raises. It does not return an empty `evidence` array, a shorter array, or chunks from a different query to fill the list.

| Situation | What happens |
| --- | --- |
| The request is not a dictionary, `ticket_body` is missing, or `ticket_body` is not a string with non-whitespace text. | `ValueError`. The store is not queried. |
| The store cannot be opened, the query raises, or the result is not five records matching the schema above. | `RuntimeError`. Nothing is substituted. |

Any exception means the call failed. A caller must not treat a raised call as retrieved evidence.
