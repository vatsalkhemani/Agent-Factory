import requests
from bs4 import BeautifulSoup

from config import SCRAPE_TIMEOUT
from models import ScrapedPage

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

NOISE_TAGS = ["nav", "footer", "header", "script", "style", "noscript", "iframe"]


def scrape_url(url: str) -> ScrapedPage:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=SCRAPE_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove noise
        for tag in soup.find_all(NOISE_TAGS):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()

        headings = []
        for level in ["h1", "h2", "h3"]:
            for h in soup.find_all(level):
                text = h.get_text(strip=True)
                if text:
                    headings.append(text)

        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 30:
                paragraphs.append(text)

        # Cap to avoid token bloat
        paragraphs = paragraphs[:30]
        headings = headings[:20]

        return ScrapedPage(
            url=url,
            title=title,
            meta_description=meta_desc,
            headings=headings,
            paragraphs=paragraphs,
            success=True,
        )
    except Exception as e:
        return ScrapedPage(
            url=url,
            title="",
            meta_description="",
            headings=[],
            paragraphs=[],
            success=False,
            error=str(e),
        )
