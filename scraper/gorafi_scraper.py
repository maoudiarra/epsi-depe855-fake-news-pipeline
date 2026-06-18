"""
gorafi_scraper.py - Scraper Le Gorafi - DEPE855
Le Gorafi expose un flux RSS. On l'utilise pour éviter les blocages.
"""

import hashlib
import requests
import xml.etree.ElementTree as ET
from datetime import datetime


def make_uid(title: str, source: str) -> str:
    return hashlib.md5(f"{source}::{title.strip().lower()}".encode()).hexdigest()


def scrape(max_items: int = 5) -> list[dict]:
    """
    Flux RSS Le Gorafi (source de satire / fake news intentionnelle).
    """
    rss_url = "https://www.legorafi.fr/feed/"
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
                "news_uid":            make_uid(title, "gorafi"),
                "title":               title,
                "summary":             summary[:500],
                "source":              "Le Gorafi",
                "publication_date":    pub_date,
                "event_date":          pub_date,
                "verification_status": "fake",
                "confidence_score":    0.02,
            })

    except Exception as e:
        print(f"[Gorafi] Erreur RSS : {e}")

    return articles


if __name__ == "__main__":
    results = scrape(5)
    if results:
        for a in results:
            print(f"❌ {a['title']}")
    else:
        print("Aucun article récupéré.")
