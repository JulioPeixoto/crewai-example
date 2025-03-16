# Imports da biblioteca padrão
import logging
import time
from typing import ClassVar, List, Optional
import hashlib
from datetime import datetime, timedelta

# Imports de terceiros
from crewai.tools import BaseTool
from serpapi import GoogleSearch
from django.core.cache import cache

# Imports locais
from api.settings import SERPER_API_KEY

logger = logging.getLogger(__name__)

# Cache local para evitar chamadas repetidas à API
SEARCH_CACHE = {}
MAX_CACHE_SIZE = 50  # Limitar o tamanho do cache
CACHE_EXPIRY = 3600  # Cache válido por 1 hora (em segundos)

class GoogleSearchWrapper(BaseTool):
    name: str = "Web Search"
    description: str = "Pesquisa noticias de tecnologia na web usando Google Search. Use apenas para informações essenciais e evite múltiplas consultas similares."
    api_key: ClassVar[str] = SERPER_API_KEY
    max_retries: ClassVar[int] = 2  
    delay_between_retries: ClassVar[int] = 2
    max_daily_searches: ClassVar[int] = 10 
    searches_today: ClassVar[int] = 0
    last_reset_date: ClassVar[str] = None
    target_sites: ClassVar[List[str]] = []

    def __init__(self, target_sites: Optional[List[str]] = None):
        super().__init__()
        if target_sites:
            self.__class__.target_sites = target_sites
            logger.info(f"Sites alvo configurados: {target_sites}")

    def _run(self, query: str) -> str:
        logger.info("=== Iniciando GoogleSearchWrapper ===")
        
        self._check_daily_limit_reset()
        
        if self.searches_today >= self.max_daily_searches:
            logger.warning(f"Limite diário de buscas atingido ({self.max_daily_searches}). Retornando mensagem de limite.")
            return "LIMITE DE BUSCAS ATINGIDO: O número máximo de buscas diárias foi alcançado. Por favor, use as informações já disponíveis ou tente novamente amanhã."
        
        if isinstance(query, dict) and 'description' in query:
            logger.info("Query é um dicionário, extraindo description")
            query = query['description']
        
        normalized_query = self._normalize_query(query)
        
        # Adiciona os sites alvo à chave de cache para diferenciar resultados
        sites_hash = ""
        if self.target_sites:
            sites_hash = hashlib.md5("".join(self.target_sites).encode()).hexdigest()[:8]
            
        cache_key = f"google_search_{sites_hash}_{hashlib.md5(normalized_query.encode()).hexdigest()}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Resultado encontrado no cache Django para query: {normalized_query[:50]}...")
            return cached_result
        
        cache_key_local = f"{sites_hash}_{normalized_query}"
        if cache_key_local in SEARCH_CACHE:
            cache_time, result = SEARCH_CACHE[cache_key_local]
            # Verificar se o cache ainda é válido
            if datetime.now() - cache_time < timedelta(seconds=CACHE_EXPIRY):
                logger.info(f"Resultado encontrado no cache local para query: {normalized_query[:50]}...")
                return result
        
        self.__class__.searches_today += 1
        logger.info(f"Busca {self.searches_today} de {self.max_daily_searches} hoje")
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Tentativa {attempt + 1} de {self.max_retries}")
                
                search_params = {
                    "q": query,
                    "api_key": self.api_key,
                    "num": 5  # Aumentado para 5 resultados
                }
                
                # Adicionar sites específicos à consulta se fornecidos
                if self.target_sites:
                    site_query = " OR ".join([f"site:{site}" for site in self.target_sites])
                    search_params["q"] = f"{query} ({site_query})"
                    logger.info(f"Consulta modificada com sites alvo: {search_params['q'][:100]}...")
                
                search = GoogleSearch(search_params)
                results = search.get_dict()
                
                if "error" in results:
                    error_msg = f"Erro na API do Google: {results['error']}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                formatted_results = []
                for result in results.get("organic_results", []):
                    title = result.get("title", "Sem título")
                    link = result.get("link", "")
                    snippet = result.get("snippet", "Sem descrição")
                    formatted_results.append(f"Título: {title}\nLink: {link}\nDescrição: {snippet}\n")
                
                result_text = "\n".join(formatted_results) if formatted_results else "Nenhum resultado encontrado para esta consulta."
                
                # Armazenar no cache Django (30 minutos)
                cache.set(cache_key, result_text, 1800)
                
                # Armazenar no cache local
                self._update_local_cache(cache_key_local, result_text)
                
                return result_text
            
            except Exception as e:
                logger.error(f"Erro na tentativa {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = self.delay_between_retries * (attempt + 1)
                    logger.warning(f"Aguardando {wait_time} segundos antes da próxima tentativa...")
                    time.sleep(wait_time)
                    continue
                logger.error(f"Todas as tentativas falharam. Último erro: {str(e)}")
                return f"Erro na busca: {str(e)}. Por favor, tente uma consulta diferente ou use as informações já disponíveis."

    def _normalize_query(self, query):
        """Normaliza a query para reduzir buscas duplicadas"""
        # Remover espaços extras e converter para minúsculas
        normalized = ' '.join(query.lower().split())
        return normalized
    
    def _update_local_cache(self, query, result):
        """Atualiza o cache local, mantendo o tamanho máximo"""
        # Adicionar novo resultado
        SEARCH_CACHE[query] = (datetime.now(), result)
        
        # Limitar o tamanho do cache
        if len(SEARCH_CACHE) > MAX_CACHE_SIZE:
            # Remover o item mais antigo
            oldest_query = min(SEARCH_CACHE.keys(), key=lambda k: SEARCH_CACHE[k][0])
            del SEARCH_CACHE[oldest_query]
    
    def _check_daily_limit_reset(self):
        """Verifica e reseta o contador diário se necessário"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if self.last_reset_date != today:
            logger.info(f"Resetando contador diário de buscas. Último reset: {self.last_reset_date}, Hoje: {today}")
            self.__class__.searches_today = 0
            self.__class__.last_reset_date = today
