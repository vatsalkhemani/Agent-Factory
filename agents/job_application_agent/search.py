import time

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from config import SCRAPE_TIMEOUT, SEARCH_RESULTS_PER_QUERY, SEARCH_DELAY, MAX_CONTENT_CHARS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
NOISE_TAGS = ["nav", "footer", "header", "script", "style", "noscript", "iframe"]


def scrape_url(url: str) -> dict:
    """Scrape a URL and return dict with title, content, success, error."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=SCRAPE_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup.find_all(NOISE_TAGS):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 30:
                paragraphs.append(text)

        content = " ".join(paragraphs[:30])
        if len(content) > MAX_CONTENT_CHARS:
            content = content[:MAX_CONTENT_CHARS] + "..."

        return {"title": title, "content": content, "success": True, "error": ""}
    except Exception as e:
        return {"title": "", "content": "", "success": False, "error": str(e)}


def search_company(company_name: str, company_url: str = "") -> dict:
    """Research a company using its URL and/or web search. Returns aggregated content."""
    all_content = []

    # Strategy 1: Scrape company website if URL provided
    if company_url:
        page = scrape_url(company_url)
        if page["success"]:
            all_content.append(f"[Company Website] {page['content']}")

        # Try /about page
        about_url = company_url.rstrip("/") + "/about"
        about_page = scrape_url(about_url)
        if about_page["success"]:
            all_content.append(f"[About Page] {about_page['content']}")

    # Strategy 2: DuckDuckGo search
    search_queries = [
        f"{company_name} company mission values culture",
        f"{company_name} recent news 2024 2025",
    ]

    for query in search_queries:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=SEARCH_RESULTS_PER_QUERY))
            for r in results:
                snippet = r.get("body", "")
                if snippet:
                    all_content.append(f"[Search: {query}] {snippet}")
            time.sleep(SEARCH_DELAY)
        except Exception as e:
            print(f"DDG search failed for '{query}': {e}")
            continue

    return {
        "content": "\n\n".join(all_content) if all_content else "",
        "success": bool(all_content),
    }
