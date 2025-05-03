FROM python:3.13.3-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.13.3-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=api.settings \
    DEBUG=False \
    PYTHONOPTIMIZE=2

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY manage.py ./
COPY api ./api
COPY news ./news
COPY static ./static
COPY templates ./templates

RUN mkdir -p /app/staticfiles /app/media

RUN python manage.py collectstatic --noinput

RUN python manage.py migrate

RUN python manage.py createsuperuser --noinput

EXPOSE 8000

CMD ["gunicorn", "api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "60", "--keep-alive", "5", "--max-requests", "1000", "--max-requests-jitter", "50"] 