"""
afp_scraper.py - Scraper AFP Fact Check - DEPE855
AFP bloque le scraping HTML (403). On utilise les flux RSS officiels.
Plusieurs URLs de fallback pour maximiser la disponibilité.
"""

import hashlib
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime


# Flux RSS AFP à essayer dans l'ordre
AFP_RSS_URLS = [
    "https://www.afp.com/fr/actus/afp_actualite/792,31,9,7,33/feed",
    "https://www.afp.com/fr/actus/afp_actualite/792,31,9,7,33,34/feed",
    "https://factuel.afp.com/list/all/rss",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "fr-FR,fr;q=0.9",
}


def make_uid(title: str, source: str) -> str:
    return hashlib.md5(f"{source}::{title.strip().lower()}".encode()).hexdigest()


def _parse_date(pub_str: str) -> str:
    try:
        return parsedate_to_datetime(pub_str).isoformat()
    except Exception:
        return datetime.utcnow().isoformat()


def _fetch_rss(url: str, max_items: int) -> list[dict]:
    """Tente de récupérer et parser un flux RSS AFP."""
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    root  = ET.fromstring(resp.content)
    items = root.findall(".//item")[:max_items]
    results = []
    for item in items:
        title   = item.findtext("title",       default="Sans titre").strip()
        summary = item.findtext("description", default="").strip()
        pub_str = item.findtext("pubDate",     default="")
        results.append({
            "news_uid":            make_uid(title, "afp_factcheck"),
            "title":               title,
            "summary":             summary[:500],
            "source":              "AFP Fact Check",
            "publication_date":    _parse_date(pub_str),
            "event_date":          _parse_date(pub_str),
            "verification_status": "verified",
            "confidence_score":    0.95,
        })
    return results


def scrape(max_items: int = 10) -> list[dict]:
    """Essaie chaque URL RSS AFP jusqu'à en trouver une qui répond."""
    for url in AFP_RSS_URLS:
        try:
            articles = _fetch_rss(url, max_items)
            if articles:
                print(f"[AFP] ✅ {len(articles)} articles via {url}")
                return articles
        except Exception as e:
            print(f"[AFP] ⚠️  {url} → {e}")

    print("[AFP] ❌ Aucun flux RSS disponible.")
    return []


if __name__ == "__main__":
    for a in scrape(5):
        print(f"✅ {a['title']}")