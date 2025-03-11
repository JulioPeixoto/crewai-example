import logging
from django.utils import timezone
from django.contrib import messages
import markdown2

from .crew import NewsCrew
from ..models import Noticia

logger = logging.getLogger(__name__)

class Noticias:
    def __init__(self):
        self.noticias = []

    def obter_todas_noticias(self):
        """Retorna todas as notícias armazenadas."""
        return self.noticias

    def gerar_noticias(self, request=None):
        """
        Gera notícias usando a NewsCrew e salva no banco de dados.
        
        Args:
            request: Objeto de requisição Django (opcional, para mensagens flash)
            
        Returns:
            Noticia: A notícia gerada e salva ou None em caso de erro
        """
        try:
            data_atual = timezone.now()
            
            news_crew = NewsCrew(data=data_atual)
            crew_results = news_crew.run()            

            if not crew_results:
                raise ValueError("Nenhum resultado gerado pelos agentes")

            content = self._processar_resultado_crew(crew_results)
            
            html_content = markdown2.markdown(content, extras=['fenced-code-blocks', 'tables'])
            
            noticia = self._salvar_noticia(html_content)
            
            self.adicionar_noticia(noticia)
            
            if request:
                messages.success(request, "Notícias geradas com sucesso!")
                
            return noticia
            
        except Exception as e:
            logger.error(f"Erro ao gerar notícias: {str(e)}", exc_info=True)
            if request:
                messages.error(request, f"Erro ao gerar notícias: {str(e)}")
            return None
    
    def _processar_resultado_crew(self, crew_results):
        """Processa o resultado do crew e retorna o conteúdo como string."""
        if hasattr(crew_results, 'raw_output'):
            return crew_results.raw_output
        elif isinstance(crew_results, (list, tuple)) and crew_results:
            return crew_results[0]
        else:
            return str(crew_results)
    
    def _salvar_noticia(self, html_content):
        """Salva a notícia no banco de dados e retorna o objeto criado."""
        try:
            noticia = Noticia.objects.create(
                texto=html_content,
                data_publicacao=timezone.now()
            )
            logger.info(f"Notícia salva com ID: {noticia.id}")
            return noticia
        except Exception as db_error:
            logger.error(f"Erro ao salvar notícia no banco: {str(db_error)}")
            raise
