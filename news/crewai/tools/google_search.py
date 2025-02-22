# Imports da biblioteca padrão
import logging
import time
from typing import ClassVar

# Imports de terceiros
from crewai.tools import BaseTool
from serpapi import GoogleSearch

# Imports locais
from api.settings import SERPER_API_KEY

logger = logging.getLogger(__name__)


class GoogleSearchWrapper(BaseTool):
    name: str = "Web Search"
    description: str = "Pesquisa na web usando Google Search"
    api_key: ClassVar[str] = SERPER_API_KEY
    max_retries: ClassVar[int] = 3
    delay_between_retries: ClassVar[int] = 2

    def _run(self, query: str) -> str:
        logger.info("=== Iniciando GoogleSearchWrapper ===")
        logger.info(f"Query recebida: {query}")
        logger.info(f"Tipo da query: {type(query)}")
        logger.info(f"API Key presente: {'Sim' if self.api_key else 'Não'}")
        
        if isinstance(query, dict) and 'description' in query:
            logger.info("Query é um dicionário, extraindo description")
            query = query['description']
            logger.info(f"Query após extração: {query}")
            
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Tentativa {attempt + 1} de {self.max_retries}")
                
                search_params = {
                    "q": query,
                    "api_key": self.api_key,
                    "num": 1
                }
                logger.info(f"Parâmetros da busca: {search_params}")
                
                search = GoogleSearch(search_params)
                logger.info("Objeto GoogleSearch criado com sucesso")
                
                results = search.get_dict()
                logger.info("Resultados obtidos da API")
                
                if "error" in results:
                    error_msg = f"Erro na API do Google: {results['error']}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                logger.info(f"Número de resultados orgânicos: {len(results.get('organic_results', []))}")
                
                formatted_results = []
                for result in results.get("organic_results", []):
                    title = result.get("title", "Sem título")
                    link = result.get("link", "")
                    snippet = result.get("snippet", "Sem descrição")
                    formatted_results.append(f"Título: {title}\nLink: {link}\nDescrição: {snippet}\n")
                
                logger.info("Resultados formatados com sucesso")
                return "\n".join(formatted_results)
            
            except Exception as e:
                logger.error(f"Erro na tentativa {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = self.delay_between_retries * (attempt + 1)
                    logger.warning(f"Aguardando {wait_time} segundos antes da próxima tentativa...")
                    time.sleep(wait_time)
                    continue
                logger.error(f"Todas as tentativas falharam. Último erro: {str(e)}")
                raise
