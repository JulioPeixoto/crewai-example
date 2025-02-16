#!/bin/bash
set -e  # Isso fará o script parar se houver algum erro
python manage.py check  # Verifica se há problemas na configuração
python manage.py migrate
python manage.py collectstatic --noinput