# Minimal News - Sistema Multiagente com CrewAI

![CrewAI Logo](static/crewai.png)

Um sistema de geração automática de notícias de tecnologia utilizando agentes de IA orquestrados pelo framework CrewAI.

## 🤖 Sistemas Multiagentes

Sistemas multiagentes são compostos por múltiplos agentes de IA que interagem em um ambiente compartilhado. Cada agente:

- Possui um papel específico e especializado
- Trabalha de forma autônoma com objetivos próprios
- Colabora com outros agentes para resolver problemas complexos
- Compartilha informações e resultados

A principal vantagem dos sistemas multiagentes é a capacidade de dividir problemas complexos em tarefas menores e especializadas, permitindo que cada agente se concentre em uma parte específica do problema.

## 🚢 CrewAI Framework

[CrewAI](https://github.com/crewAIInc/crewAI) é um framework de código aberto para orquestrar agentes de IA em fluxos de trabalho colaborativos. Principais características:

- **Agentes Especializados**: Cada agente tem um papel, objetivo e conjunto de ferramentas específicos
- **Fluxos de Trabalho**: Orquestração de tarefas sequenciais ou paralelas
- **Ferramentas Integradas**: Acesso a APIs, pesquisa web e outras capacidades
- **Memória Compartilhada**: Compartilhamento de informações entre agentes

O CrewAI gerencia a comunicação entre agentes e garante que cada um receba os inputs necessários para realizar sua tarefa, criando um sistema coeso e eficiente.

## 📰 Sistema de Geração de Notícias

O Minimal News utiliza um sistema multiagente baseado no CrewAI para gerar notícias de tecnologia de forma autônoma. O fluxo de trabalho é composto por três agentes especializados:

### Agentes

1. **Pesquisador**: Inicia o processo buscando notícias tecnológicas relevantes. Utiliza a API do Google Search para encontrar informações atuais.

2. **Analista**: Recebe os resultados da pesquisa e analisa as tendências e implicações das notícias. Cria um contexto mais amplo para cada aspecto.

3. **Redator**: Transforma as análises em artigos coesos. Cada ângulo da notícia principal é desenvolvido em um texto independente.

### Fluxo de Tarefas

O processo segue um fluxo bem definido:

```
Pesquisar Notícias → Análise de Tendências → Redigir Notícias → Revisar e Consolidar
```

1. **Pesquisar Notícias**: Busca notícias relevantes de tecnologia e identifica diferentes ângulos para exploração.
2. **Análise de Tendências**: Analisa as tendências tecnológicas emergentes relacionadas às notícias.
3. **Redigir Notícias**: Cria artigos em markdown a partir das notícias, cada um explorando um aspecto diferente.
4. **Revisar e Consolidar**: Revisa, formata e consolida os artigos em um único documento coeso.

## 🔧 Tecnologias Utilizadas

- **CrewAI**: Framework para orquestração de agentes
- **LangChain**: Biblioteca para construção de aplicações com LLMs
- **Django**: Framework web para o backend
- **Celery**: Sistema de filas para tarefas assíncronas
- **PostgreSQL** (NeonDB): Banco de dados SQL
- **Redis**: Cache e broker para o Celery
- **Docker**: Containerização da aplicação
- **Heroku**: Plataforma de deploy

## 🚀 Como Contribuir

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Conta na OpenAI (para API key)
- Conta na Serper (para API key de pesquisa)

### Configuração Local

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/crewai-example.git
cd crewai-example
```

2. **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:

```
DEBUG=True
SECRET_KEY=sua-chave-secreta
POSTGRES_DATABASE=minimal_news
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
OPENAI_API_KEY=sua-chave-openai
SERPER_API_KEY=sua-chave-serper
```

3. **Inicie os containers com Docker**

```bash
docker-compose up -d
```

4. **Acesse a aplicação**

Abra seu navegador e acesse `http://localhost:8000`

### Executando Tarefas

Para gerar notícias manualmente:

```bash
docker-compose exec web python manage.py gerar_noticias
```

Para especificar sites de pesquisa:

```bash
docker-compose exec web python manage.py gerar_noticias --sites wired.com techcrunch.com
```

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

---

Desenvolvido com ❤️ usando CrewAI e Django
