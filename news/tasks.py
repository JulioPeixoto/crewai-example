from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def gerar_noticias_automaticas():
    """
    Tarefa para gerar notícias automaticamente.
    Esta tarefa pode ser agendada para execução periódica.
    """
    logger.info("Iniciando geração automática de notícias")
    # Aqui você pode adicionar a lógica para gerar notícias automaticamente
    # Por exemplo, chamar funções que já existem no seu projeto
    
    # from .utils import gerar_noticias
    # resultado = gerar_noticias()
    
    logger.info("Geração automática de notícias concluída")
    return True 