import streamlit as st
import requests

st.title("🔍 Perplexity API Search")
st.write(
    "This app uses Perplexity's API to search the web with domain filtering capabilities. "
    "You can allowlist or blocklist specific domains to focus your search results."
)

with st.sidebar:
    st.header("🎯 Domain Filtering")
    
    filter_type = st.radio(
        "Filter Type:",
        ["None", "Allowlist", "Blocklist"],
        help="Allowlist: Only search these domains. Blocklist: Exclude these domains from search.",
        index=1
    )
    
    if filter_type != "None":
        default_domains = "sec.gov" if filter_type == "Allowlist" else ""
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
            
            if filter_type == "Blocklist":
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

    if query := st.text_input("Enter your search query:", placeholder="What would you like to search for?"):
        
        search_domains = []
        if filter_type != "None" and 'domains' in locals():
            search_domains = domains
        
        with st.spinner("Searching..."):
            try:
                url = "https://api.perplexity.ai/chat/completions"
                
                payload = {
                    "model": "llama-3.1-sonar-small-128k-online",
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
