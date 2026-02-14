import requests
from bs4 import BeautifulSoup

# Fetches the HTML content of a given URL and extracts the article title and all paragraph text
def scrape_article(url: str, timeout: int = 10) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        # Sends an HTTP GET request to the URL with a safety timeout
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status() # Raises an error if the request failed 

        print(f"Status Code: {r.status_code}")

        # Parses the HTML content
        soup = BeautifulSoup(r.text, "html.parser")

        # Extracts the page title or sets a default if not found
        title = soup.title.get_text(strip=True) if soup.title else "No title"

        # Collects text from all <p> tags and joins them into a single string
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        text = "\n".join([p for p in paragraphs if p])

        print(f"Extracted Text: {text[:500]}...") 

        return {"url": url, "title": title, "text": text}
    except Exception as e:
        # Returns basic info with empty text if any error occurs during scraping
        print(f"Error while scraping {url}: {e}")
        return {"url": url, "title": "N/A", "text": ""}