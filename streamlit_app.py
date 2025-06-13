demo_domains = """sec.gov
macromicro.me
"""
demo_query = """針對2025-06-12市場行情的創高及創低項目進行分析，歸納列點，以利簡訊通知

2025-06-12 市場行情
------外匯------
美元指數 ：97.8300 --- T1: -0.8010 (-0.81%) 2022-03-31以來最低
歐元/美元 ：1.1586 --- T1: 0.0075 (0.65%) 2021-11-10以來最高
英鎊/美元 ：1.3614 --- T1: 0.0047 (0.35%) 2022-01-18以來最高
澳幣/美元 ：0.6531 --- T1: 0.0022 (0.34%) 2024-11-25以來最高
美元/台幣 ：29.8075 --- T1: -0.1125 (-0.38%) 2023-02-04以來最高
美元/加幣 ：1.3603 --- T1: -0.0063 (-0.46%) 2024-10-07以來最高
------歐股------
英國-FTSE 100 ：8885 --- T1: 21 (0.23%) 1984-01-03以來最高
------亞股------
南韓 - Korea Stock Exchange KOSPI Index ：2920 --- T1: 13 (0.45%) 2022-01-17以來最高
------美股------
美國-S&P 500 ：6045 --- T1: 23 (0.38%) 2025-02-21以來最高
道瓊工業指數 ：42968 --- T1: 102 (0.24%) 2025-03-06以來最高
美國-費城半導體指數 ：5249 --- T1: 17 (0.32%) 2025-02-21以來最高"""

import streamlit as st
import requests

st.title("🔍 Perplexity API Search")
st.write(
    "This app uses Perplexity's API to search the web with domain filtering capabilities. "
    "You can allowlist or denylist specific domains to focus your search results."
)

with st.sidebar:
    st.header("🤖 Model Settings")
    
    model = st.selectbox(
        "Search Model:",
        [
            "sonar-reasoning",
            "sonar-reasoning-pro",
            "sonar-deep-research",
        ],
        index=0,
        help="Choose the Perplexity model for search",
    )
    
    if model != "sonar-reasoning":
        st.warning("⚠️ Due to cost considerations, only sonar-reasoning is available for now. If you want to try `sonar-reasoning-pro` or `sonar-deep-research`, please contact PHIL.")
        model = "sonar-reasoning"
    
    st.info(f"🎯 Using: **{model}**")
    
    st.markdown("[📊 View Pricing](https://docs.perplexity.ai/guides/pricing)")
    
    st.header("🎯 Domain Filtering")
    
    filter_type = st.radio(
        "Filter Type:",
        ["None", "Allowlist", "Denylist"],
        help="Allowlist: Only search these domains. Denylist: Exclude these domains from search.",
        index=1
    )
    
    if filter_type != "None":
        default_domains = demo_domains if filter_type == "Allowlist" else ""
        domains_input = st.text_area(
            f"Enter domains (one per line, max 10):",
            value=default_domains,
            placeholder="example.com\nwikipedia.org\nnasa.gov",
            help="Enter simple domain names without 'https://' or 'www.'"
        )
        
        if domains_input:
            domains = [domain.strip() for domain in domains_input.split('\n') if domain.strip()]
            if len(domains) > 10:
                st.warning("⚠️ Maximum 10 domains allowed. Only first 10 will be used.")
                domains = domains[:10]
            
            if filter_type == "Denylist":
                domains = [f"-{domain}" for domain in domains]
            
            st.write(f"**Active domains ({len(domains)}):**")
            for domain in domains:
                st.write(f"• {domain}")

try:
    perplexity_api_key = st.secrets["PPLX_API_KEY"]
except KeyError:
    st.error("Please add PPLX_API_KEY to .streamlit/secrets.toml", icon="🗝️")
    st.stop()

if perplexity_api_key:
    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    for entry in st.session_state.search_history:
        with st.expander(f"🔍 {entry['query']}", expanded=False):
            if entry.get('domains'):
                st.write(f"**Domains:** {', '.join(entry['domains'])}")
            st.markdown(entry['response'])
            if entry.get('citations'):
                st.markdown("**Sources:**")
                for i, citation in enumerate(entry['citations'], 1):
                    st.markdown(f"[{i}] {citation}")

    query = st.text_area("Enter your search query:", value=demo_query, placeholder=demo_query, height=450)
    
    if st.button("🔍 Search", type="primary"):
        if query:
            search_domains = []
            if filter_type != "None" and 'domains' in locals():
                search_domains = domains
            
            with st.spinner("Searching..."):
                try:
                    url = "https://api.perplexity.ai/chat/completions"
                    
                    payload = {
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful search assistant. Provide comprehensive and accurate information based on the search results."
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ]
                    }
                    
                    if search_domains:
                        payload["search_domain_filter"] = search_domains
                    
                    headers = {
                        "Authorization": f"Bearer {perplexity_api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    response = requests.post(url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result['choices'][0]['message']['content']
                        
                        # Process citations if available
                        citations = result.get('citations', [])
                        if citations:
                            # Replace citation numbers with hyperlinks
                            processed_answer = answer
                            for i, citation in enumerate(citations, 1):
                                citation_pattern = f"[{i}]"
                                if citation_pattern in processed_answer:
                                    citation_link = f"[[{i}]]({citation})"
                                    processed_answer = processed_answer.replace(citation_pattern, citation_link)
                            answer = processed_answer
                        
                        search_entry = {
                            'query': query,
                            'response': answer,
                            'domains': search_domains if search_domains else None,
                            'citations': citations if citations else None
                        }
                        st.session_state.search_history.append(search_entry)
                        
                        st.markdown("### 📄 Search Results")
                        if search_domains:
                            st.info(f"🎯 Filtered by domains: {', '.join(search_domains)}")
                        st.markdown(answer)
                        
                        # Display citations if available
                        if citations:
                            st.markdown("### 📚 Sources")
                            for i, citation in enumerate(citations, 1):
                                st.markdown(f"[{i}] {citation}")
                        
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    if st.session_state.search_history and st.button("🗑️ Clear History"):
        st.session_state.search_history = []
        st.rerun()
