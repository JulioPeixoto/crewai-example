import os
from celery import Celery
import logging

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

app = Celery('api')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Configurações adicionais para otimização
app.conf.update(
    worker_prefetch_multiplier=1,  # Evita que workers peguem muitas tarefas de uma vez
    task_acks_late=True,  # Confirma tarefas apenas após conclusão bem-sucedida
    task_reject_on_worker_lost=True,  # Rejeita tarefas se o worker morrer
    task_time_limit=3600,  # Limite de tempo de 1 hora para tarefas
    worker_max_tasks_per_child=200,  # Reinicia worker após 200 tarefas para evitar vazamentos de memória
    broker_connection_retry_on_startup=True,  # Tenta reconectar ao broker na inicialização
)

# Descobrir tarefas automaticamente
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tarefa para debug do Celery"""
    logger.info(f'Request: {self.request!r}')
    