FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY producer.py .

ENV KAFKA_BOOTSTRAP_SERVERS=localhost:9092

CMD ["python", "producer.py"]
