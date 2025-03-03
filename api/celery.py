import os
from celery import Celery

# Definir o módulo de configurações padrão do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

app = Celery('api')

# Usar configurações do Django para o Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carregar tarefas automaticamente de todos os arquivos tasks.py registrados
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 