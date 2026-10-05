import re

import pandas as pd
import requests
from bs4 import BeautifulSoup


MAJOR_WIKI_URLS = {
    "computer science": "https://en.wikipedia.org/wiki/Computer_science",
    "artificial intelligence": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "information systems": "https://en.wikipedia.org/wiki/Information_systems",
    "data science": "https://en.wikipedia.org/wiki/Data_science",
    "cyber security": "https://en.wikipedia.org/wiki/Computer_security",
}


def _clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_web_scraping(majors, timeout, logger):
    """Scrape public Wikipedia pages to enrich students with major descriptions."""
    logger.info("Web scraping extraction started")
    rows = []
    session = requests.Session()
    session.headers.update({
        "User-Agent": "StudentDataPipeline/1.0 (educational project)"
    })

    for major in sorted({str(m).strip() for m in majors if pd.notna(m)}):
        key = major.lower()
        url = MAJOR_WIKI_URLS.get(key)
        if not url:
            rows.append({
                "major": major,
                "web_title": pd.NA,
                "web_summary": pd.NA,
                "web_url": pd.NA,
            })
            continue

        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find("h1")
            paragraph = next(
                (p for p in soup.select("p") if _clean_text(p.get_text(" ", strip=True))),
                None,
            )
            summary = _clean_text(paragraph.get_text(" ", strip=True)) if paragraph else ""
            rows.append({
                "major": major,
                "web_title": _clean_text(title.get_text(" ", strip=True)) if title else major,
                "web_summary": summary[:500],
                "web_url": url,
            })
            logger.info("Scraped web metadata for major: %s", major)
        except requests.RequestException as exc:
            logger.warning("Web scraping failed for %s: %s", major, exc)
            rows.append({
                "major": major,
                "web_title": pd.NA,
                "web_summary": pd.NA,
                "web_url": url,
            })

    result = pd.DataFrame(rows, columns=["major", "web_title", "web_summary", "web_url"])
    logger.info("Web scraping records: %s", len(result))
    return result
