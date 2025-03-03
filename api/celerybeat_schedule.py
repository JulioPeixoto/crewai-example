from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'gerar-noticias-diariamente': {
        'task': 'news.tasks.gerar_noticias_automaticas',
        'schedule': crontab(hour=8, minute=0),
        'args': (),
    },
}