# Routing service contract

`RoutingService.route_ticket` classifies one ticket body. The classifier is loaded once in `__init__` and reused. This is the Homework 3 router that Homework 4 kept: the Homework 2 cleaner, word TF-IDF, and logistic regression with `C=1.0`.

The request does not include a department, a model path, or a workflow id. The service does not summarize the ticket.

## Request

`route_ticket` accepts one dictionary.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `ticket_body` | string | yes | The ticket `Body`, unchanged. Must contain at least one non-whitespace character. A Boolean, a number, or `null` is not a string. |

Other fields are ignored. The service does not read them and does not require them.

```json
{
  "ticket_body": "The invoice for account 4412 does not match last month."
}
```

## Response

A successful call returns one dictionary with exactly these fields. Both come from the classifier. The service does not rename them, drop a department, or replace the scores.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `recommended_department` | string | yes | Exactly one of the ten departments below. Its score in `class_scores` is greater than or equal to every other score. |
| `class_scores` | object | yes | Exactly the ten departments below, each mapped to one finite number. No missing department, no extra key, and no Boolean. |

Departments:

- `Billing and Payments`
- `Customer Service`
- `General Inquiry`
- `Human Resources`
- `IT Support`
- `Product Support`
- `Returns and Exchanges`
- `Sales and Pre-Sales`
- `Service Outages and Maintenance`
- `Technical Support`

```json
{
  "recommended_department": "Billing and Payments",
  "class_scores": {
    "Billing and Payments": 0.62,
    "Customer Service": 0.04,
    "General Inquiry": 0.03,
    "Human Resources": 0.02,
    "IT Support": 0.05,
    "Product Support": 0.04,
    "Returns and Exchanges": 0.03,
    "Sales and Pre-Sales": 0.04,
    "Service Outages and Maintenance": 0.06,
    "Technical Support": 0.07
  }
}
```

The numbers above are only a shape example. A real response uses the classifier's probabilities.

## Errors

The method raises. It does not return a default department, an empty score map, or a dictionary with an `error` field.

| Situation | What happens |
| --- | --- |
| The request is not a dictionary, `ticket_body` is missing, or `ticket_body` is not a string with non-whitespace text. | `ValueError`. The classifier is not called. |
| The saved model cannot be loaded, prediction raises, or the classifier output is not the response schema above. | `RuntimeError`. Nothing is substituted. |

Any exception means the call failed. A caller must not treat a raised call as a route.
