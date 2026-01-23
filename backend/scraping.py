import requests
from bs4 import BeautifulSoup


def scrape_article(url: str, timeout: int = 10) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()

        
        print(f"Status Code: {r.status_code}")

        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.get_text(strip=True) if soup.title else "No title"
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        text = "\n".join([p for p in paragraphs if p])

        print(f"Extracted Text: {text[:500]}...") 

        return {"url": url, "title": title, "text": text}
    except Exception as e:
        print(f"Error while scraping {url}: {e}")
        return {"url": url, "title": "N/A", "text": ""}