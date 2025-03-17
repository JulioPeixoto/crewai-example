import logging
from celery import shared_task
from django.utils import timezone
from typing import List, Optional

from .crewai.noticias import Noticias

logger = logging.getLogger(__name__)

@shared_task(
    name="news.tasks.gerar_noticias_automaticas",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutos
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=3600,  # 1 hora
    retry_jitter=True
)
def gerar_noticias_automaticas(self, sites: Optional[List[str]] = None):
    """
    Tarefa Celery para gerar notícias automaticamente.
    
    Args:
        sites: Lista opcional de sites para pesquisar notícias
        
    Returns:
        int: ID da notícia gerada ou None em caso de erro
    """
    try:
        logger.info(f"Iniciando geração automática de notícias às {timezone.now()}")
        
        if sites:
            logger.info(f"Sites alvo configurados: {sites}")
        
        gerador = Noticias(target_sites=sites)
        noticia = gerador.gerar_noticias()
        
        if noticia:
            logger.info(f"Notícia gerada com sucesso. ID: {noticia.id}")
            return noticia.id
        else:
            logger.error("Falha ao gerar notícia: nenhum objeto retornado")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao gerar notícias: {str(e)}", exc_info=True)
        raise self.retry(exc=e)