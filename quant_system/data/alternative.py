"""Alternative data sources such as news, social sentiment and macro data."""

import logging
from typing import Dict, List, Optional

import requests

try:
    import polars as pl
except ImportError:  # pragma: no cover
    pl = None

try:
    from bs4 import BeautifulSoup
except Exception:  # pragma: no cover
    BeautifulSoup = None


class AlternativeDataEngine:
    """Collects and processes alternative data."""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_news_sentiment(self, query: str) -> Dict:
        """Placeholder for news sentiment analysis."""
        self.logger.debug("get_news_sentiment called")
        return {"mean_sentiment": 0.0}

    def analyze_sentiment_simple(self, text: str) -> float:
        """Return a naive sentiment score for a Turkish headline.

        The function counts occurrences of a few positive and negative
        keywords and returns ``positive_count - negative_count``.  It is
        intentionally lightweight but provides a numeric signal that can be
        used as a model feature.
        """

        text_l = text.lower()
        positive = [
            "anlaşma",
            "rekor",
            "kâr",
            "yüksek",
            "artış",
            "büyüme",
            "yatırım",
            "onay",
            "kazan",
            "başarı",
        ]
        negative = [
            "zarar",
            "dava",
            "iptal",
            "düşüş",
            "soruşturma",
            "ceza",
            "kayıp",
            "gerileme",
            "risk",
            "borç",
        ]

        pos_count = sum(text_l.count(word) for word in positive)
        neg_count = sum(text_l.count(word) for word in negative)
        return float(pos_count - neg_count)

    def get_social_sentiment(self, query: str) -> Dict:
        """Placeholder for social media sentiment."""
        self.logger.debug("get_social_sentiment called")
        return {"mean_sentiment": 0.0}

    def fetch_kap_headlines(
        self, tickers: List[str], max_items: int = 5
    ) -> Optional["pl.DataFrame"]:
        """Fetch latest headlines from KAP for the given tickers."""
        if pl is None or BeautifulSoup is None:
            self.logger.error("polars and beautifulsoup4 are required")
            return None

        rows = []
        for t in tickers:
            url = f"https://www.kap.org.tr/en/sirket-bilgileri/ozet/{t.split('.')[0]}"
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                items = soup.find_all("li")[:max_items]
                for li in items:
                    headline = " ".join(li.stripped_strings)
                    rows.append({"ticker": t, "headline": headline})
            except Exception as exc:  # pragma: no cover - network dependent
                self.logger.warning("KAP scrape failed for %s: %s", t, exc)

        if not rows:
            return None
        return pl.from_dicts(rows)
