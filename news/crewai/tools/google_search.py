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
        for attempt in range(self.max_retries):
            try:
                search = GoogleSearch({
                    "q": query,
                    "api_key": self.api_key,
                    "num": 5  
                })
                results = search.get_dict()
                
                if "error" in results:
                    raise Exception(f"Erro na API do Google: {results['error']}")
                
                formatted_results = []
                for result in results.get("organic_results", []):
                    title = result.get("title", "Sem título")
                    link = result.get("link", "")
                    snippet = result.get("snippet", "Sem descrição")
                    formatted_results.append(f"Título: {title}\nLink: {link}\nDescrição: {snippet}\n")
                
                return "\n".join(formatted_results)
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.delay_between_retries * (attempt + 1)
                    logger.warning(f"Erro na pesquisa. Aguardando {wait_time} segundos antes de tentar novamente...")
                    time.sleep(wait_time)
                    continue
                logger.error(f"Erro após {self.max_retries} tentativas: {str(e)}")
                raise
