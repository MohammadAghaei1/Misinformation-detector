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
    model = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    hf_client = _get_hf_client()
    tavily = _get_tavily_client()

    # Dynamic RAG
    search_context = ""
    try:
        # search the web to see if other sources confirm the text from your scraper
        search_results = tavily.search(query=text[:200], search_depth="basic", max_results=3)
        for res in search_results['results']:
            # Use snippet for high-quality context without massive token usage
            context_piece = res.get('snippet', res['content'][:300])
            search_context += f"- Source: {res['title']}\n  Key Info: {context_piece}\n"
    except Exception as e:
        search_context = "Search failed, rely on logic."

    # This prompt tells Llama to stop saying "I don't know" and start comparing facts
    if is_url:
        role_instruction = "You are a professional fact-checker analyzing a scraped article."
    else:
        role_instruction = "You are a professional fact-checker analyzing a raw text claim."

    # Refined prompt with strict logical verification rules
    prompt = f"""
    {role_instruction}
    Current Date: February 2026.
    
    SEARCH CONTEXT (Real-time facts from the web):
    {search_context}

    INPUT TEXT TO VERIFY:
    {text[:1000]}

    INSTRUCTIONS:
    1. Extract the specific claim made in the INPUT TEXT.
    2. Check the SEARCH CONTEXT to see if it supports or contradicts this claim.
    3. STRICT LABELING RULES:
       - If the SEARCH CONTEXT confirms the claim is a LIE, HOAX, or FALSE (e.g. if the search says someone is alive but the claim says they are dead), you MUST label it 'fake'.
       - Only label 'real' if the SEARCH CONTEXT confirms the claim is 100% accurate.
       - If there is no clear evidence either way, label 'uncertain'.
    4. Trust the SEARCH CONTEXT above your own internal training data.
    5. The 'explanation' must justify the 'label' based ONLY on the SEARCH CONTEXT provided.

    Return ONLY JSON:
    {{
      "label": "fake" or "real" or "uncertain",
      "confidence": (0-100),
      "explanation": "State the evidence found in the search context and conclude if the claim is true or false."
    }}
    """

    # Get Llama's verdict
    try:
        resp = hf_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=350
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