import os
from unittest import result
import requests

from langchain.tools import tool
from dotenv import load_dotenv
from tavily import TavilyClient
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

from rich import print  # formatar saida no terminal


import tavily

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILI_API_KEY"))


@tool
def consulta_web(query: str) -> str:
    """
    Busca na web fontes recentes e confiáveis sobre o tema informado.
    Retorna títulos, URLs e trechos resumidos.
    """
    resultados = tavily.search(query=query, max_results=5)  # type: ignore

    # print(resultados)

    fontes_encontradas = []

    for resultado in resultados["results"]:
        fontes_encontradas.append(
            f"Título: {resultado['title']}\n"
            f"URL: {resultado['url']}\n"
            f"Trecho: {resultado['content'][:500]}\n"
        )

    return "\n---\n".join(fontes_encontradas)


@tool
def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable content from a URL.
    Uses multiple extraction strategies for better reliability.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        # ── Fetch page ─────────────────────────────────────
        response = requests.get(url, headers=headers, timeout=15)

        response.raise_for_status()

        html = response.text

        # ──────────────────────────────────────────────────
        # Strategy 1 → trafilatura (BEST for articles/blogs)
        # ──────────────────────────────────────────────────
        extracted = trafilatura.extract(
            html, include_comments=False, include_tables=False
        )

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r"\s+", " ", extracted)
            return cleaned[:5000]

        # ──────────────────────────────────────────────────
        # Strategy 2 → readability
        # ──────────────────────────────────────────────────
        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup(
            ["script", "style", "nav", "footer", "header", "aside", "form"]
        ):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:
            cleaned = re.sub(r"\s+", " ", text)
            return cleaned[:5000]

        # ──────────────────────────────────────────────────
        # Strategy 3 → fallback full page extraction
        # ──────────────────────────────────────────────────
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(
            ["script", "style", "nav", "footer", "header", "aside", "form"]
        ):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        cleaned = re.sub(r"\s+", " ", text)

        if cleaned:
            return cleaned[:5000]

        return "Could not extract meaningful content from the page."

    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."

    except requests.exceptions.HTTPError as e:
        return f"HTTP error occurred: {str(e)}"

    except Exception as e:
        return f"Could not scrape URL: {str(e)}"


@tool
def scrapping_url(url: str) -> str:
    """
    Acessa uma URL e tenta extrair o conteúdo principal da página em texto limpo.

    A função foi escrita para não quebrar a execução do agente.
    Quando uma página bloqueia o acesso, demora demais ou não possui conteúdo útil,
    a ferramenta retorna uma mensagem controlada em vez de lançar erro.
    """

    limite_caracteres = 5000
    tamanho_minimo_conteudo = 200
    timeout_requisicao = 20

    tags_para_remover = [
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
        "noscript",
        "iframe",
        "svg",
    ]

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
    }

    def limpar_texto(texto: str) -> str:
        """Remove espaços duplicados, quebras de linha e tabulações."""
        return re.sub(r"\s+", " ", texto).strip()

    def texto_eh_util(texto: str | None) -> bool:
        """Verifica se o texto extraído tem conteúdo mínimo para ser útil."""
        return bool(texto and len(texto.strip()) > tamanho_minimo_conteudo)

    def remover_ruidos(soup: BeautifulSoup) -> None:
        """Remove tags que normalmente não fazem parte do conteúdo principal."""
        for tag in soup(tags_para_remover):
            tag.decompose()

    if not url.startswith(("http://", "https://")):
        return "URL inválida. Informe uma URL começando com http:// ou https://."

    try:
        session = requests.Session()

        response = session.get(
            url,
            headers=headers,
            timeout=timeout_requisicao,
            allow_redirects=True,
        )

        if response.status_code == 403:
            return (
                "Não foi possível acessar esta página porque o site bloqueou "
                "requisições automáticas. O servidor retornou 403 Forbidden. "
                "Tente usar outra URL ou outra fonte."
            )

        if response.status_code == 404:
            return (
                "Não foi possível acessar esta página porque ela não foi encontrada. "
                "O servidor retornou 404."
            )

        if response.status_code == 429:
            return (
                "Não foi possível acessar esta página porque o site limitou muitas "
                "requisições em pouco tempo. O servidor retornou 429 Too Many Requests."
            )

        if response.status_code >= 400:
            return (
                f"Não foi possível acessar esta página. "
                f"O servidor retornou o status HTTP {response.status_code}."
            )

        html = response.text

        if not html or len(html.strip()) < 100:
            return (
                "A página foi acessada, mas não retornou HTML suficiente para extração."
            )

        # Estratégia 1: Trafilatura
        try:
            conteudo = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=False,
            )

            if texto_eh_util(conteudo):
                return limpar_texto(conteudo)[:limite_caracteres]  # type: ignore

        except Exception:
            pass

        # Estratégia 2: Readability
        try:
            documento = Document(html)
            html_principal = documento.summary()

            soup = BeautifulSoup(html_principal, "html.parser")
            remover_ruidos(soup)

            texto = soup.get_text(separator=" ", strip=True)

            if texto_eh_util(texto):
                return limpar_texto(texto)[:limite_caracteres]

        except Exception:
            pass

        # Estratégia 3: BeautifulSoup como fallback
        try:
            soup = BeautifulSoup(html, "html.parser")
            remover_ruidos(soup)

            texto = soup.get_text(separator=" ", strip=True)
            texto_limpo = limpar_texto(texto)

            if texto_eh_util(texto_limpo):
                return texto_limpo[:limite_caracteres]

        except Exception:
            pass

        return (
            "A página foi acessada, mas não foi possível extrair um conteúdo "
            "textual relevante. O conteúdo pode estar em JavaScript, exigir login "
            "ou estar protegido contra scraping."
        )

    except requests.exceptions.Timeout:
        return (
            "Não foi possível acessar a URL porque a requisição demorou demais "
            "e atingiu o limite de tempo."
        )

    except requests.exceptions.ConnectionError:
        return (
            "Não foi possível acessar a URL por erro de conexão. "
            "Verifique se o endereço está correto e acessível."
        )

    except requests.exceptions.InvalidURL:
        return "A URL informada é inválida."

    except requests.exceptions.RequestException as error:
        return f"Não foi possível acessar a URL. Detalhe técnico: {str(error)}"

    except Exception as error:
        return f"Não foi possível processar esta URL. Detalhe técnico: {str(error)}"
