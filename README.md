# 🔍 Perplexity API Search

A Streamlit app that provides web search functionality using Perplexity's API with advanced domain filtering capabilities.

## Features

- **Web Search**: Search the web using Perplexity's powerful AI models
- **Domain Filtering**: Filter search results by specific domains
- **Allowlist Mode**: Search only within specified domains (up to 10)
- **Blocklist Mode**: Exclude specific domains from search results
- **Search History**: View and manage your previous searches
- **Clean Interface**: Easy-to-use Streamlit interface

## How to run it on your own machine

1. Get a Perplexity API key from [here](https://www.perplexity.ai/settings/api)

2. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

3. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

4. Enter your Perplexity API key in the app interface

## Domain Filtering Usage

### Allowlist (Search only these domains)
- Enter domains like: `wikipedia.org`, `nasa.gov`, `space.com`
- Results will only come from these sources

### Blocklist (Exclude these domains)
- Enter domains like: `pinterest.com`, `reddit.com`, `quora.com`  
- Results will exclude these sources

### Best Practices
- Use simple domain names (e.g., `example.com`)
- Avoid protocol prefixes like `https://` or `www.`
- Maximum of 10 domains per filter
- Main domains automatically cover subdomains
