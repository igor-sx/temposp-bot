![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![License](https://img.shields.io/github/license/yourusername/yourrepo)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-informational) ![Google Cloud](https://img.shields.io/badge/Hosted%20on-Google%20Cloud-blue) ![atproto](https://img.shields.io/badge/atproto-bluesky-1da1f2) ![Last Commit](https://img.shields.io/github/last-commit/yourusername/yourrepo)
### English (Portuguese below)

This Python script automates posting weather updates to Bluesky with a little help of AI (LLM) for summarization of text.

**How it works:**

1.  **Scrapes Data:**
    *   It fetches the latest news text from the CGE SP news page (`https://www.cgesp.org/v3//noticias.jsp`) using `requests` and `BeautifulSoup`.
    *   It extracts the URL of the current illustrative weather condition image from the CGE SP weather station page (`https://www.cgesp.org/v3//estacoes-meteorologicas.jsp`) by parsing CSS rules found in a `<style>` tag using `BeautifulSoup` and regular expressions.
2.  **Summarizes News:**
    *   The scraped news text is sent to the OpenAI API (`gpt-4o-mini` at the moment).
    *   A specific prompt instructs the model to generate a concise summary (300 characters) in Brazilian Portuguese, highlighting key weather information and any alerts, suitable for a microblog post.
3.  **Downloads Image:**
    *   The script downloads the image file identified in step 1.
4.  **Posts to Bluesky:**
    *   Using the `atproto` library, the script logs into Bluesky.
    *   It creates a new post containing the generated summary and attaches the downloaded weather image.
5.  **Execution & Configuration:**
    *   The script requires `BLUESKY_USERNAME`, `BLUESKY_PASSWORD`, and `OPENAI_API_KEY` to be set as environment variables.
    *   It includes extensive logging for monitoring.
    *   It can be run locally for testing or deployed as a Google Cloud Function (`cloud_entry_point`) designed to be triggered periodically (e.g., by Google Cloud Scheduler).

**Motivation:** A personal project for learning Python and libraries related to web scraping, generative artificial intelligence, and the use of Google Cloud Platform (GCP) and its tools: Cloud Scheduler, Cloud Functions—aiming for security through the use of Secret Manager and efficiency through low resource usage.
---

### Versão em Português

Este script em Python automatiza a publicação de atualizações meteorológicas no Bluesky com uma pequena ajuda de IA (LLM) pra resumir notícias.

**Como funciona:**

1.  **Coleta de Dados:**
    *   Busca o texto da notícia mais recente na página de notícias do CGE SP (`https://www.cgesp.org/v3//noticias.jsp`) usando `requests` e `BeautifulSoup`.
    *   Extrai a URL da imagem da condição meteorológica atual da página de estações meteorológicas do CGE SP (`https://www.cgesp.org/v3//estacoes-meteorologicas.jsp`) analisando regras CSS encontradas em uma tag `<style>` com `BeautifulSoup` e expressões regulares.
2.  **Resumo da Notícia:**
    *   O texto da notícia coletado é enviado para a API da OpenAI (`gpt-4o-mini`, atualmente).
    *   Um prompt específico instrui o modelo a gerar um resumo conciso (cerca de 300 caracteres) em Português (Brasil), destacando informações meteorológicas chave e quaisquer alertas, adequado para um post de microblog como Bluesky ou Twitter.
3.  **Download da Imagem:**
    *   O script baixa o arquivo de imagem identificado na etapa 1 e o mantém na memória.
4.  **Publicação no Bluesky:**
    *   Usando a biblioteca `atproto`, o script faz login no Bluesky.
    *   Cria um novo post contendo o resumo gerado e anexa a imagem ilustrativa meteorológica baixada.
5.  **Execução e Configuração:**
    *   O script requer que `BLUESKY_USERNAME`, `BLUESKY_PASSWORD`, e `OPENAI_API_KEY` sejam definidas como variáveis de ambiente.
    *   Inclui logs detalhados para monitoramento.
    *   Pode ser executado localmente para testes ou implantado como uma Google Cloud Function (`cloud_entry_point`), projetada para ser acionada periodicamente (por exemplo, pelo Google Cloud Scheduler).

**Objetivo:** Fornecer atualizações meteorológicas resumidas e oportunas, acompanhadas de uma imagem ilustrativa, em uma conta da rede social Bluesky.

**Motivação:** projeto pessoal de aprendizado de Python e bibliotecas de scraping, de inteligência artificial generativa e de uso da Google Cloud Platform (GCP) e de suas ferramentas: Cloud Scheduler, Cloud Functions, buscando segurança com uso de Secret Manager e eficiência com baixo uso de recursos. 

---
