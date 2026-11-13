FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY router_api.py .
COPY assignment6 ./assignment6
COPY assignment3 ./assignment3

EXPOSE 8000

CMD ["uvicorn", "router_api:app", "--host", "0.0.0.0", "--port", "8000"]
