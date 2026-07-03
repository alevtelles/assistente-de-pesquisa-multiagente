## Fluxo geral

```text
Tema de pesquisa
↓
Agente de Busca
↓
Tavily API
↓
state['resultado_busca']
↓
Agente Leitor
↓
BeautifulSoup
↓
state['conteudo_extraido']
↓
Cadeia de Escrita
↓
Cadeia de Crítica
↓
Saída Final
```

---

# 1. Você fornece um Tema de Pesquisa

## O que faz

É a entrada inicial do sistema. O usuário informa o assunto que deseja pesquisar.

Exemplo:

```text
Quais são as tendências de IA generativa para atendimento ao cliente em 2026?
```

## Para onde vai

Esse tema é enviado para o **Agente de Busca**.

## Como vai

Normalmente vai como uma variável de entrada do fluxo, algo parecido com:

```python
state = {
    "tema": "tendências de IA generativa para atendimento ao cliente"
}
```

Esse `state` começa pequeno e vai sendo preenchido durante o workflow.

---

# 2. Primeiro Agente: Agente de Busca

## O que faz

O **Agente de Busca** recebe o tema e decide buscar informações na internet.

Ele não escreve o relatório ainda. A função dele é apenas encontrar fontes relevantes.

Ele pode procurar por:

```text
artigos recentes
notícias
documentações
relatórios
posts técnicos
fontes confiáveis
```

## Para onde vai

Ele envia a solicitação para uma ferramenta externa chamada **Tavily API**.

## Como vai

O agente transforma o tema em uma busca mais objetiva.

Exemplo:

```text
Buscar fontes recentes sobre IA generativa no atendimento ao cliente em 2026
```

Depois ele chama a ferramenta de busca.

---

# 3. Ferramenta 1: Tavily API

## O que faz

A **Tavily API** é uma ferramenta externa de busca na web.

Ela acessa a internet e retorna resultados em tempo real.

Ela pode trazer:

```text
título da página
URL
resumo
trechos relevantes
data
fonte
```

## Para onde vai

O resultado da Tavily volta para o **Agente de Busca**.

Depois é salvo no estado do fluxo:

```python
state["resultado_busca"]
```

## Como vai

A Tavily retorna uma lista de fontes. Exemplo simplificado:

```python
state["resultado_busca"] = [
    {
        "titulo": "Relatório sobre IA no atendimento",
        "url": "https://exemplo.com/relatorio-ia",
        "resumo": "O artigo fala sobre uso de LLMs em atendimento..."
    },
    {
        "titulo": "Tendências de GenAI para empresas",
        "url": "https://exemplo.com/genai-empresas",
        "resumo": "Texto sobre automação, agentes e suporte..."
    }
]
```

---

# 4. state['resultado_busca'] salvo

## O que faz

Esse bloco representa a memória temporária onde o resultado da busca foi salvo.

O `state` é como uma mochila que carrega as informações de uma etapa para outra.

## Para onde vai

Esse resultado vai para o **Agente Leitor**.

## Como vai

O Agente Leitor acessa o conteúdo salvo em:

```python
state["resultado_busca"]
```

Ele lê as URLs encontradas e decide quais páginas precisam ser abertas para extrair mais conteúdo.

---

# 5. Segundo Agente: Agente Leitor

## O que faz

O **Agente Leitor** pega os links encontrados pelo Agente de Busca e acessa as páginas para extrair o conteúdo real.

Ele não depende só do resumo da busca. Ele tenta entrar nas fontes e capturar mais informação.

A função dele é:

```text
abrir URLs
ler páginas
extrair conteúdo relevante
limpar ruído
separar informação útil
```

## Para onde vai

Ele envia as URLs para a ferramenta **BeautifulSoup**.

## Como vai

Ele pega cada item salvo em `state["resultado_busca"]` e passa para a ferramenta de raspagem.

Exemplo:

```python
urls = [
    item["url"] for item in state["resultado_busca"]
]
```

Depois chama a ferramenta para extrair o conteúdo das páginas.

---

# 6. Ferramenta 2: BeautifulSoup

## O que faz

O **BeautifulSoup** é usado para fazer scraping de páginas web.

Ele abre o HTML da página e extrai o texto útil.

Ele pode remover:

```text
menus
rodapés
propagandas
scripts
códigos HTML
elementos visuais desnecessários
```

E tenta manter:

```text
títulos
parágrafos
listas
conteúdo principal
links relevantes
```

## Para onde vai

O conteúdo extraído volta para o **Agente Leitor**.

Depois é salvo em:

```python
state["conteudo_extraido"]
```

## Como vai

Exemplo simplificado:

```python
state["conteudo_extraido"] = [
    {
        "url": "https://exemplo.com/relatorio-ia",
        "conteudo": "A IA generativa vem sendo usada em atendimento..."
    },
    {
        "url": "https://exemplo.com/genai-empresas",
        "conteudo": "Empresas estão adotando agentes inteligentes..."
    }
]
```

---

# 7. state['conteudo_extraido'] salvo

## O que faz

Esse é um dos pontos mais importantes do fluxo.

Aqui o sistema já tem o conteúdo real das fontes, não apenas os links.

Esse estado contém a matéria-prima que será usada para escrever o relatório.

## Para onde vai

Esse conteúdo vai para duas etapas:

```text
Cadeia de Escrita
Cadeia de Crítica
```

## Como vai

O fluxo passa o conteúdo extraído para as chains seguintes.

Exemplo:

```python
writer_input = state["conteudo_extraido"]
critic_input = state["conteudo_extraido"]
```

Na prática, a Cadeia de Escrita usa esse conteúdo para produzir o relatório, e a Cadeia de Crítica pode usar o mesmo conteúdo para verificar se o relatório está fiel às fontes.

---

# 8. Cadeia de Escrita

## O que faz

A **Cadeia de Escrita** transforma o conteúdo bruto em um relatório organizado.

Ela pega vários textos soltos e cria uma resposta com estrutura.

Pode gerar algo como:

```text
Introdução
Contexto
Principais descobertas
Análise
Riscos
Oportunidades
Conclusão
Fontes
```

## Para onde vai

O relatório criado vai para a **Cadeia de Crítica** ou direto para a composição da saída final.

## Como vai

A chain recebe o conteúdo extraído e um prompt de escrita.

Exemplo conceitual:

```python
relatorio = writer_chain.invoke({
    "tema": state["tema"],
    "conteudo": state["conteudo_extraido"]
})
```

Depois salva:

```python
state["relatorio"] = relatorio
```

---

# 9. Cadeia de Crítica

## O que faz

A **Cadeia de Crítica** revisa o relatório.

Ela age como um avaliador sênior. O papel dela não é pesquisar novamente, mas avaliar a qualidade do que foi produzido.

Ela pode verificar:

```text
se o relatório responde ao tema
se há informações fracas
se faltam detalhes
se há contradições
se o texto está claro
se precisa de melhoria
se as fontes foram bem aproveitadas
```

## Para onde vai

A crítica pode ir para dois caminhos:

```text
corrigir/melhorar o relatório
ou compor a saída final
```

## Como vai

Ela recebe o relatório e, se necessário, o conteúdo original.

Exemplo:

```python
avaliacao = critic_chain.invoke({
    "tema": state["tema"],
    "relatorio": state["relatorio"],
    "fontes": state["conteudo_extraido"]
})
```

Depois pode salvar:

```python
state["avaliacao"] = avaliacao
```

Essa avaliação pode conter nota, feedback e sugestões.

---

# 10. Saída Final

## O que faz

A **Saída Final** é o resultado entregue ao usuário.

Ela junta o relatório escrito com as melhorias ou validações feitas pela Cadeia de Crítica.

O resultado pode ser:

```text
relatório final
resumo executivo
análise técnica
lista de fontes
recomendações
pontos de atenção
```

## Para onde vai

Vai para o usuário.

## Como vai

O sistema monta a resposta final usando o que foi salvo no estado:

```python
final_output = {
    "tema": state["tema"],
    "relatorio": state["relatorio"],
    "avaliacao": state["avaliacao"]
}
```

Ou, em texto:

```text
Aqui está o relatório final revisado sobre o tema pesquisado...
```

---

# O papel do `state`

O `state` é o coração do fluxo.

Ele permite que cada etapa compartilhe informações com a próxima.

Sem o `state`, cada agente ficaria isolado.

Com o `state`, o sistema funciona como uma equipe:

```python
state = {
    "tema": "...",
    "resultado_busca": "...",
    "conteudo_extraido": "...",
    "relatorio": "...",
    "avaliacao": "...",
    "saida_final": "..."
}
```

Ele não é necessariamente uma memória permanente. É mais uma memória de execução, usada enquanto o workflow está rodando.

---

# O que cada cor representa

**Verde**
Entrada e saída do sistema.
Exemplo: tema da pesquisa e relatório final.

**Roxo**
Agentes autônomos.
Exemplo: Agente de Busca e Agente Leitor.

**Vermelho**
Ferramentas externas.
Exemplo: Tavily API e BeautifulSoup.

**Laranja**
Estado do fluxo.
É onde os dados intermediários são armazenados.

**Cinza**
Cadeias de processamento.
São etapas que processam, escrevem, revisam ou transformam informação.

---

# Explicação simples

Esse sistema é como uma equipe de pesquisa:

```text
Você pede um tema.

Um pesquisador busca fontes na internet.

Outro pesquisador lê as páginas e extrai o conteúdo importante.

Um redator escreve o relatório.

Um revisor avalia a qualidade.

O sistema entrega o relatório final.
```

A diferença é que tudo isso é feito com agentes de IA, ferramentas externas e um estado compartilhado coordenado pelo LangChain.
