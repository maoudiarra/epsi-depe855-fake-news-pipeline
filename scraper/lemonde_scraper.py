"""
lemonde_scraper.py - Scraper Le Monde - DEPE855
Le Monde bloque aussi le scraping HTML. On utilise leur flux RSS officiel.
"""

import hashlib
import requests
import xml.etree.ElementTree as ET
from datetime import datetime


def make_uid(title: str, source: str) -> str:
    return hashlib.md5(f"{source}::{title.strip().lower()}".encode()).hexdigest()


def scrape(max_items: int = 10) -> list[dict]:
    """
    Flux RSS Le Monde - page d'accueil (public, sans restriction).
    """
    rss_url = "https://www.lemonde.fr/rss/une.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }
    articles = []
    try:
        resp = requests.get(rss_url, headers=headers, timeout=10)
        resp.raise_for_status()

        root = ET.fromstring(resp.content)

        for item in root.findall(".//item")[:max_items]:
            title   = item.findtext("title", default="Sans titre").strip()
            summary = item.findtext("description", default="").strip()
            pub_str = item.findtext("pubDate", default="")

            try:
                from email.utils import parsedate_to_datetime
                pub_date = parsedate_to_datetime(pub_str).isoformat()
            except Exception:
                pub_date = datetime.utcnow().isoformat()

            articles.append({
                "news_uid":            make_uid(title, "lemonde"),
                "title":               title,
                "summary":             summary[:500],
                "source":              "Le Monde",
                "publication_date":    pub_date,
                "event_date":          pub_date,
                "verification_status": "pending",
                "confidence_score":    None,
            })

    except Exception as e:
        print(f"[Le Monde] Erreur RSS : {e}")

    return articles


if __name__ == "__main__":
    results = scrape(5)
    if results:
        for a in results:
            print(f"📰 {a['title']}")
    else:
        print("Aucun article récupéré.")
