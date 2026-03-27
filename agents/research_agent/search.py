import time

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from config import SCRAPE_TIMEOUT, SEARCH_RESULTS_PER_QUERY, SEARCH_DELAY, MAX_CONTENT_CHARS
from models import SearchResult, ScrapedPage

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
NOISE_TAGS = ["nav", "footer", "header", "script", "style", "noscript", "iframe"]


def scrape_url(url: str) -> ScrapedPage:
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

        return ScrapedPage(url=url, title=title, content=content, success=True)
    except Exception as e:
        return ScrapedPage(url=url, title="", content="", success=False, error=str(e))


def web_search(query: str, max_results: int = SEARCH_RESULTS_PER_QUERY) -> list[SearchResult]:
    """Search DuckDuckGo and scrape top results. Falls back to snippets on scrape failure."""
    results = []

    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        print(f"DuckDuckGo search failed for '{query}': {e}")
        return results

    for r in raw_results:
        url = r.get("href", "")
        title = r.get("title", "")
        snippet = r.get("body", "")

        # Try to scrape the page for richer content
        page = scrape_url(url)
        if page.success and page.content:
            content = page.content
            success = True
        else:
            # Fallback: use the DDG snippet (always have something)
            content = snippet
            success = bool(snippet)

        results.append(SearchResult(
            query=query,
            url=url,
            title=title or page.title,
            snippet=snippet,
            content=content,
            success=success,
        ))

        # Small delay between scrapes to be polite
        time.sleep(0.3)

    return results
