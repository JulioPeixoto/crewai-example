from celery import shared_task
from celery.utils.log import get_task_logger
from news.crewai.noticias import Noticias

logger = get_task_logger(__name__)

@shared_task
def gerar_noticias_automaticas():
    logger.info("Iniciando geração automática de notícias")
    noticias = Noticias()
    noticias.gerar_noticias()
    logger.info("Geração automática de notícias concluída")
    return True