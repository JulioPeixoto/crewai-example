import yaml
import os
from dotenv import load_dotenv
from crewai import Crew, Agent, Task
from langchain_community.tools import DuckDuckGoSearchRun
from crewai.tools import BaseTool

load_dotenv()

class DuckDuckGoSearchWrapper(BaseTool):
    name: str = "Web Search"
    description: str = "Pesquisa na web usando DuckDuckGo"

    def _run(self, query: str) -> str:
        search = DuckDuckGoSearchRun()
        return search.run(query)
    

class NewsCrew:
    def __init__(self):
        self.load_config()
        self.setup_tools()
        self.setup_agents()
        self.setup_tasks()

    def load_config(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        agents_path = os.path.join(base_path, 'config', 'agents.yml')
        tasks_path = os.path.join(base_path, 'config', 'tasks.yml')
        
        with open(agents_path, 'r', encoding='utf-8') as f:
            self.agents_config = yaml.safe_load(f)
        with open(tasks_path, 'r', encoding='utf-8') as f:
            self.tasks_config = yaml.safe_load(f)

    def setup_tools(self):
        search = DuckDuckGoSearchWrapper()
        self.tools = {
            'web_search': search
        }

    def setup_agents(self):
        self.agents = {}
        for agent_id, config in self.agents_config.items():
            self.agents[agent_id] = Agent(
                name=config['name'],
                role=config['role'],
                goal=config['goal'],
                backstory=config['backstory'],
                verbose=True,
                allow_delegation=False,
                tools=[self.tools['web_search']]
            )

    def setup_tasks(self):
        self.tasks = []
        for task in self.tasks_config['tasks']:
            if not isinstance(task, dict): continue
            
            agent = self.agents.get(task['agent'])
            if not agent: continue
                
            task_tools = []
            for tool in task.get('tool', []):
                if tool in self.tools: task_tools.append(self.tools[tool])
            
            context = task.get('context', [])
            
            if isinstance(context, str): context = [context]
            elif not isinstance(context, list): context = []
                
            self.tasks.append(Task(
                description=task['description'],
                agent=agent,
                expected_output=task['expected_output'],
                tools=task_tools,
                context=context
            ))

    def run(self):
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            verbose=2
        )
        result = crew.kickoff()
        return result
