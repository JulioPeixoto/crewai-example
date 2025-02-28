FROM python:3.11-slim AS builder

# Configurar variáveis de ambiente para otimização
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copiar apenas os arquivos necessários para instalar dependências
COPY requirements.txt .

# Instalar dependências em uma camada separada
RUN pip install --no-cache-dir --user -r requirements.txt

# Segunda etapa - imagem final
FROM python:3.11-slim

# Configurar variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/log/ \
    && touch /var/log/cron.log

WORKDIR /app

# Copiar as dependências instaladas da etapa anterior
COPY --from=builder /root/.local /root/.local

# Copiar o código da aplicação
COPY . .

# Configurar o crontab
RUN if [ -f crontab ]; then \
    cp crontab /etc/cron.d/scheduler-cron && \
    chmod 0644 /etc/cron.d/scheduler-cron && \
    crontab /etc/cron.d/scheduler-cron; \
    fi

# Tornar o script scheduler.sh executável
RUN chmod +x scheduler.sh

# Expor a porta que o Django usa
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["gunicorn", "api.wsgi:application", "--bind", "0.0.0.0:8000"] 