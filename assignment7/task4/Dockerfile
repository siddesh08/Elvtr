FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WORKFLOW_LOG_PATH=/logs/traces.jsonl \
    ROUTING_URL=http://host.docker.internal:8001 \
    RETRIEVAL_URL=http://host.docker.internal:8002 \
    OLLAMA_URL=http://host.docker.internal:8003

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY workflow_api.py .
COPY assignment6 ./assignment6

EXPOSE 8000

CMD ["uvicorn", "workflow_api:app", "--host", "0.0.0.0", "--port", "8000"]
