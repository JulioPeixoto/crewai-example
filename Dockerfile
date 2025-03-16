FROM python:3.11-slim AS builder

# Configurar variáveis de ambiente para otimização
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Instalar dependências de compilação necessárias para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas os arquivos necessários para instalar dependências
COPY requirements.txt .

# Instalar dependências em uma camada separada
RUN pip install --no-cache-dir --user -r requirements.txt

# Segunda etapa - imagem final (mais leve)
FROM python:3.11-slim

# Configurar variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=api.settings \
    DEBUG=False \
    PYTHONOPTIMIZE=2

# Instalar apenas as dependências do sistema absolutamente necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar as dependências instaladas da etapa anterior
COPY --from=builder /root/.local /root/.local

# Copiar apenas os arquivos necessários para a aplicação
COPY manage.py ./
COPY api ./api
COPY news ./news
COPY static ./static
COPY templates ./templates

# Criar diretórios para arquivos estáticos e mídia
RUN mkdir -p /app/staticfiles /app/media

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expor a porta que o Django usa
EXPOSE 8000

# Comando para iniciar a aplicação com configurações otimizadas
CMD ["gunicorn", "api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "60", "--keep-alive", "5", "--max-requests", "1000", "--max-requests-jitter", "50"] 