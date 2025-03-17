from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    # 'gerar-noticias-diariamente': {
    #     'task': 'news.tasks.gerar_noticias_automaticas',
    #     'schedule': crontab(hour=8, minute=0),  # Executa todos os dias às 8h
    #     'args': (),
    #     'options': {'expires': 3600}  # Expira após 1 hora
    # },
    'gerar-noticias-semanalmente': {
        'task': 'news.tasks.gerar_noticias_automaticas',
        'schedule': crontab(hour=8, minute=0, day_of_week=5),  # Executa toda sexta-feira às 8h
        'args': (),
        'kwargs': {'sites': ['wired.com', 'techcrunch.com', 'engadget.com', 'theverge.com']},
        'options': {'expires': 3600}  # Expira após 1 hora
    },
}