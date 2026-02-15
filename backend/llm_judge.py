import os
import re
import json
from tavily import TavilyClient
from huggingface_hub import InferenceClient

# Initializes and returns a TavilyClient using the API key from environment variables
def _get_tavily_client():
    tavily_key = os.getenv("TAVILY_API_KEY")
    return TavilyClient(api_key=tavily_key)

# Initializes and returns a HuggingFace InferenceClient using the provided HF token
def _get_hf_client():
    return InferenceClient(token=os.getenv("HF_TOKEN"))

# Performs RAG-based misinformation analysis by searching real-time web data
def judge_news(text: str, is_url: bool = False) -> dict:
    model = os.getenv("HF_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
    hf_client = _get_hf_client()
    tavily = _get_tavily_client()

    # Dynamic RAG
    search_context = ""
    try:
        # search the web to see if other sources confirm the text from your scraper
        search_results = tavily.search(query=text[:200], search_depth="basic", max_results=2)
        for res in search_results['results']:
            # Truncate content to 400 chars to avoid memory overflow
            content_snippet = res['content'][:400]
            search_context += f"- Source: {res['title']}\n  Fact: {content_snippet}\n"
    except Exception as e:
        search_context = "Search failed, rely on logic."

    # This prompt tells Llama to stop saying "I don't know" and start comparing facts
    if is_url:
        role_instruction = "You are analyzing a scraped article from a URL."
    else:
        role_instruction = "You are analyzing a raw text claim."

    prompt = f"""
    {role_instruction}
    Current Date: January 2026.
    
    SEARCH CONTEXT (Real-time facts from the web):
    {search_context}

    INPUT TEXT TO VERIFY:
    {text[:1000]}

    INSTRUCTIONS:
    1. Compare the INPUT TEXT with the SEARCH CONTEXT.
    2. If the SEARCH CONTEXT confirms the events, label it 'real'.
    3. If there is a direct contradiction or no major news outlet reports this, label it 'fake'.
    4. Trust the SEARCH CONTEXT more than your internal memory.

    Return ONLY JSON:
    {{
      "label": "fake" or "real" or "uncertain",
      "confidence": (0-100),
      "explanation": "Briefly explain the alignment or contradiction found."
    }}
    """

    # Get Llama's verdict
    try:
        resp = hf_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300
        )
        raw_content = resp.choices[0].message.content.strip()
    except Exception as e:
        return {"label": "uncertain", "confidence": 0, "explanation": f"Model inference failed: {str(e)}"}

    # Keep your existing re.search and json.loads logic here
    try:
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        return json.loads(json_match.group())
    except:
        return {"label": "uncertain", "confidence": 0, "explanation": "Logic analysis failed."}