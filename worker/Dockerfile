FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        libreoffice \
        libreoffice-writer \
        libreoffice-calc \
        libreoffice-impress \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

CMD ["celery", "-A", "converto_worker.bootstrap.celery_app", "worker", "--loglevel=info"]
