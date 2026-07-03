import os
from unittest import result
import requests

from langchain.tools import tool
from dotenv import load_dotenv
from tavily import TavilyClient
from rich import print  # formatar saida no terminal


import tavily

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILI_API_KEY"))


def consulta_web(query: str) -> str:
    """
    Pesquise na web informações recentes e confiáveis sobre o tema. Retorna títulos, URLs e trechos resumidos.
    """
    resultados = tavily.search(query=query, max_results=5)  # type: ignore

    # print(resultados)

    out = []

    for r in resultados["results"]:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:500]}\n"
        )

    return "\n---\n".join(out)
