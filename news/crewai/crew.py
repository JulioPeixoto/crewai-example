from crewai import Crew, Agent, Task
from langchain_community.tools import DuckDuckGoSearchRun
import yaml
from dotenv import load_dotenv

load_dotenv()

class NewsCrew:
    def __init__(self):
        self.load_config()
        self.setup_tools()
        self.setup_agents()
        self.setup_tasks()

    def load_config(self):
        with open('config/agents.yml', 'r') as f:
            self.agents_config = yaml.safe_load(f)
        with open('config/tasks.yml', 'r') as f:
            self.tasks_config = yaml.safe_load(f)

    def setup_tools(self):
        search = DuckDuckGoSearchRun()
        self.tools = {
            'web_search': search
        }

    def setup_agents(self):
        self.agents = {}
        for agent_id, config in self.agents_config.items():
            self.agents[agent_id] = Agent(
                name=config['name'],
                role=config['role'],
                goal=config['goals'],
                backstory=config['backstory'],
                verbose=True,
                allow_delegation=False
            )

    def setup_tasks(self):
        self.tasks = []
        for task in self.tasks_config['tasks']:
            agent = self.agents[task['agent']]
            task_tools = [self.tools[tool] for tool in task.get('tools', [])]
            
            self.tasks.append(Task(
                description=task['description'],
                agent=agent,
                expected_output=task['expected_output'],
                tools=task_tools,
                context=task.get('context', '')
            ))

    def run(self):
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            verbose=2
        )
        result = crew.kickoff()
        return result
