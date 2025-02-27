#!/bin/bash

# Configurar o crontab
cp /app/crontab /etc/cron.d/scheduler-cron
chmod 0644 /etc/cron.d/scheduler-cron
crontab /etc/cron.d/scheduler-cron

# Iniciar o serviço cron
service cron start

# Manter o contêiner em execução
tail -f /var/log/cron.log 