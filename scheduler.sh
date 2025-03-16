#!/bin/bash

# Script para ser executado pelo Heroku Scheduler
# Recomendado agendar para rodar diariamente de manhã

echo "Iniciando geração automática de notícias..."

# Lista de sites para pesquisar
SITES="wired.com engadget.com techcrunch.com theverge.com"

python manage.py gerar_noticias --quantidade=1 --ignorar-erros --sites $SITES

echo "Processo de geração de notícias concluído." 