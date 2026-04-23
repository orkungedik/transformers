# Dockerfile - SAP ABAP AI Assistant

FROM python:3.10-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodu
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Model dizini
RUN mkdir -p /models

# Port
EXPOSE 8000

# Environment variables
ENV MODEL_PATH=/models/Qwen-Coder-7B-Instruct
ENV PYTHONUNBUFFERED=1

# Çalıştır
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
