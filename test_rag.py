import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def test_search(query):
    print(f"Searching for: {query}...")
    try:
        response = tavily.search(query=query, search_depth="advanced", max_results=3)
        
        for i, result in enumerate(response['results']):
            print(f"\nSource {i+1}: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Content snippet: {result['content'][:200]}...")
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    test_search("Is the news about gas price reduction in Italy true?")