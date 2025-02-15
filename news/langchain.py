import os
from typing import List

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from api.settings import MODEL

load_dotenv()

class TitleGenerator:
    def __init__(self):
        self.model = ChatOpenAI(
            model=MODEL,
            temperature=0.6,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt = PromptTemplate.from_template("""
            Você é um editor especializado em criar títulos chamativos e informativos para notícias de tecnologia.
            
            Para cada notícia fornecida, crie um título em português que seja:
            1. Conciso (máximo 100 caracteres)
            2. Informativo
            3. Atraente para o leitor
            4. Fiel ao conteúdo
            
            Notícia:
            {text}
            
            Retorne apenas o título, sem aspas ou formatação adicional.
        """)

    def create_title(self, text: str) -> str:
        chain = self.prompt | self.model
        return chain.invoke({"text": text})
    