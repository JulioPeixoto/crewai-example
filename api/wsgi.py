"""
WSGI config for api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Configura a variável de ambiente para o módulo de configurações
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Cria a aplicação WSGI
application = get_wsgi_application()

# Certifique-se que esta linha está presente e que 'application' está definido
