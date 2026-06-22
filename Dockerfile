FROM python:3.11-slim

WORKDIR /app

# Keep image lean and deterministic: only install runtime deps.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

CMD ["python", "src/smoke_test.py"]
