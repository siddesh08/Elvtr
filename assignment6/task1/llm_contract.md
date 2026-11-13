# LLM service contract

`LLMClient.call_llm` sends one prompt to the Ollama chat API and returns the model text. It is not a summarizer. The caller supplies the prompt, the model, the generation settings, and any output schema on every call. The service does not store those, and it does not fill in a model, a temperature, a seed, or a schema when the request omits them.

The Ollama URL is stored in `__init__` and reused. It is not a request field. The service calls Ollama. It does not load the model into Python.

## Request

`call_llm` accepts one dictionary.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `prompt` | string | yes | The full text for this call. Must contain at least one non-whitespace character. The service sends it as the user message and does not wrap it in another instruction. |
| `model` | string | yes | Non-empty Ollama model name. Forwarded as given. |
| `stream` | boolean | yes | Forwarded as given. |
| `options` | object | yes | Generation settings, forwarded as given. Keys the caller does not set are not added. An empty object is valid. Values are the numbers, strings, or Booleans Ollama accepts for that key. |
| `format` | object or `null` | no | Ollama structured-output schema. Omitted or `null` means the request has no `format`. When present, it must be a JSON Schema object and it is forwarded as given. |

Other fields are ignored.

```json
{
  "prompt": "Reply with a JSON object.",
  "model": "qwen2.5:1.5b-instruct-q4_K_M",
  "stream": false,
  "options": {
    "temperature": 0,
    "seed": 42,
    "num_predict": 512
  },
  "format": {
    "type": "object",
    "properties": {
      "summary": {"type": "string"}
    },
    "required": ["summary"]
  }
}
```

The example is one legal call. A different prompt, model, or schema is still this same request.

## Response

A successful call returns one dictionary with exactly one field. The service does not parse the text and does not check it against `format`.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `content` | string | yes | The Ollama message content, unchanged. Must contain at least one non-whitespace character. |

```json
{
  "content": "{\"summary\": \"The invoice total does not match the usage export.\"}"
}
```

## Errors

The method raises. It does not return an empty string, a placeholder summary, or a previous call's text.

| Situation | What happens |
| --- | --- |
| The request is not a dictionary, a required field is missing, or a field has the wrong type or an empty `prompt` or `model`. | `ValueError`. Ollama is not called. |
| `format` is present and is not `null` or an object. | `ValueError`. Ollama is not called. |
| The connection fails, Ollama returns a non-success status, the body is not the expected chat object, or `message.content` is missing or blank. | `RuntimeError`. Nothing is substituted. |

Any exception means the call failed. A caller must not treat a raised call as model output.
