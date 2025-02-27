#!/bin/bash

# Script para ser executado pelo Heroku Scheduler
# Recomendado agendar para rodar diariamente de manhã

echo "Iniciando geração automática de notícias..."
python manage.py gerar_noticias --quantidade=1
echo "Processo de geração de notícias concluído." 