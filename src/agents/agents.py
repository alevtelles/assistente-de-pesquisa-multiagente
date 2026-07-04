from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rich import prompt
from src.tools.tools import consulta_web, scrape_url, scrapping_url
from dotenv import load_dotenv

load_dotenv()

# Inicialização do modelo
llm = ChatOpenAI(model="gpt-4o-minit", temperature=0)


# Agente de pesquisa
def agente_pesquisa():
    return create_agent(
        model=llm,
        tools=[consulta_web],
    )


# Agente de leitura
def agente_leitura():
    return create_agent(
        model=llm,
        tools=[scrape_url],
    )


# Geração do relatório de pesquisa

prompt_relatorio_pesquisa = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Você é um especialista em redação de relatórios de pesquisa. Sua função é transformar informações coletadas em um relatório claro, bem estruturado, factual e profissional.",
        ),
        (
            "human",
            """Escreva um relatório de pesquisa detalhado sobre o tema abaixo.

            Tema: {topic}

            Conteúdo da pesquisa coletada: {research}

            Estruture o relatório com as seguintes seções:

            1. Introdução: Apresente o contexto do tema e explique por que ele é relevante.
            2. Principais descobertas: Liste no mínimo 3 descobertas importantes, explicando cada uma com clareza e profundidade.
            3. Conclusão: Resuma os principais aprendizados e apresente uma visão final sobre o tema.
            4. Fontes: Liste todas as URLs encontradas no conteúdo da pesquisa.

            O relatório deve ser detalhado, factual, bem organizado e escrito em tom profissional.""",
        ),
    ]
)

gerar_relatorio_de_pesquisa = prompt_relatorio_pesquisa | llm | StrOutputParser()


# critic_chain
critic_prompt = ChatPromptTemplate.from_messages([])
