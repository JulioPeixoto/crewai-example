import yaml
import os
from dotenv import load_dotenv
from crewai import Crew, Agent, Task
from langchain_community.tools import DuckDuckGoSearchRun
from crewai.tools import BaseTool
import logging
from pprint import pformat

# Configuração do logger do Django
logger = logging.getLogger(__name__)

load_dotenv()

class DuckDuckGoSearchWrapper(BaseTool):
    name: str = "Web Search"
    description: str = "Pesquisa na web usando DuckDuckGo"

    def _run(self, query: str) -> str:
        try:
            logger.debug(f"Executando pesquisa: {query}")
            search = DuckDuckGoSearchRun()
            result = search.run(query)
            logger.debug(f"Resultado da pesquisa: {result[:200]}...")
            return result
        except Exception as e:
            logger.error(f"Erro na pesquisa DuckDuckGo: {str(e)}", exc_info=True)
            raise

class NewsCrew:
    def __init__(self):
        try:
            logger.info("Iniciando NewsCrew")
            self.load_config()
            self.setup_tools()
            self.setup_agents()
            self.setup_tasks()
            logger.info("NewsCrew inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro na inicialização do NewsCrew: {str(e)}", exc_info=True)
            raise

    def load_config(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            agents_path = os.path.join(base_path, 'config', 'agents.yml')
            tasks_path = os.path.join(base_path, 'config', 'tasks.yml')
            
            logger.info(f"Carregando configurações de: {agents_path} e {tasks_path}")
            
            with open(agents_path, 'r', encoding='utf-8') as f:
                self.agents_config = yaml.safe_load(f)
                logger.debug(f"Configuração dos agentes carregada: \n{pformat(self.agents_config)}")
            
            with open(tasks_path, 'r', encoding='utf-8') as f:
                self.tasks_config = yaml.safe_load(f)
                logger.debug(f"Configuração das tarefas carregada: \n{pformat(self.tasks_config)}")
        except Exception as e:
            logger.error(f"Erro ao carregar arquivos de configuração: {str(e)}", exc_info=True)
            raise

    def setup_tools(self):
        try:
            search = DuckDuckGoSearchWrapper()
            self.tools = {
                'web_search': search
            }
            logger.info("Ferramentas configuradas com sucesso")
            logger.debug(f"Ferramentas disponíveis: {list(self.tools.keys())}")
        except Exception as e:
            logger.error(f"Erro na configuração das ferramentas: {str(e)}", exc_info=True)
            raise

    def setup_agents(self):
        self.agents = {}
        try:
            for agent_id, config in self.agents_config.items():
                logger.info(f"Configurando agente: {agent_id}")
                logger.debug(f"Configuração do agente {agent_id}: \n{pformat(config)}")
                
                self.agents[agent_id] = Agent(
                    name=config['name'],
                    role=config['role'],
                    goal=config['goal'],
                    backstory=config['backstory'],
                    verbose=True,
                    allow_delegation=False,
                    tools=[self.tools['web_search']]
                )
            logger.info(f"Total de {len(self.agents)} agentes configurados")
            logger.debug(f"Agentes configurados: {list(self.agents.keys())}")
        except Exception as e:
            logger.error(f"Erro na configuração dos agentes: {str(e)}", exc_info=True)
            raise

    def setup_tasks(self):
        self.tasks = []
        try:
            logger.debug(f"Iniciando configuração das tarefas. Tipo de tasks_config: {type(self.tasks_config)}")
            logger.debug(f"Conteúdo de tasks_config: \n{pformat(self.tasks_config)}")
            
            for task in self.tasks_config['tasks']:
                logger.debug(f"Processando tarefa: {pformat(task)}")
                
                if not isinstance(task, dict):
                    logger.warning(f"Tarefa ignorada - formato inválido. Tipo: {type(task)}, Valor: {task}")
                    continue
                
                agent = self.agents.get(task['agent'])
                if not agent:
                    logger.warning(f"Tarefa ignorada - agente '{task['agent']}' não encontrado. Agentes disponíveis: {list(self.agents.keys())}")
                    continue
                    
                task_tools = []
                for tool in task.get('tools', []):
                    if tool in self.tools:
                        task_tools.append(self.tools[tool])
                        logger.debug(f"Ferramenta '{tool}' adicionada à tarefa")
                    else:
                        logger.warning(f"Ferramenta '{tool}' não encontrada. Ferramentas disponíveis: {list(self.tools.keys())}")
                
                context = task.get('context', [])
                
                if isinstance(context, str):
                    context = [context]
                    logger.debug("Contexto convertido de string para lista")
                elif not isinstance(context, list):
                    context = []
                    logger.debug("Contexto inválido convertido para lista vazia")
                
                self.tasks.append(Task(
                    description=task['description'],
                    agent=agent,
                    expected_output=task['expected_output'],
                    tools=task_tools,
                    context=context
                ))
            
            logger.info(f"Total de {len(self.tasks)} tarefas configuradas")
        except Exception as e:
            logger.error(f"Erro na configuração das tarefas: {str(e)}", exc_info=True)
            raise

    def run(self):
        try:
            logger.info("Iniciando execução da crew")
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=self.tasks,
                verbose=2
            )
            logger.debug("Crew configurada, iniciando kickoff")
            result = crew.kickoff()
            logger.info("Execução da crew finalizada com sucesso")
            logger.debug(f"Resultado: {result[:200]}...")
            return result
        except Exception as e:
            logger.error(f"Erro durante a execução da crew: {str(e)}", exc_info=True)
            raise
