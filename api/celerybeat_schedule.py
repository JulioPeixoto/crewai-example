from celery.schedules import crontab

# Definição de tarefas periódicas
CELERYBEAT_SCHEDULE = {
    'gerar-noticias-diariamente': {
        'task': 'news.tasks.gerar_noticias_automaticas',
        'schedule': crontab(hour=8, minute=0),  # Executa todos os dias às 8h
        'args': (),
    },
} 