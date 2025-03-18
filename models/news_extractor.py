# models/news_extractor.py
import json
import time
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from newspaper.configuration import Configuration
import re

from utils import clean_text, make_request, log_error, load_from_cache, save_to_cache
import config

class NewsExtractor:
    """Improved news extractor with real news sources"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": config.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.news_config = Configuration()
        self.news_config.fetch_images = False
        self.news_config.memoize_articles = False
        self.news_config.request_timeout = 15

    def extract_news(self, company: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """Improved extraction with real news sources"""
        cache_key = f"news_{company}_{max_articles}"
        if cached := load_from_cache(cache_key):
            return cached

        try:
            # Try NewsAPI first (register at newsapi.org for API key)
            articles = self._newsapi_search(company, max_articles)
            if not articles:
                # Fallback to Google News RSS
                articles = self._google_news_rss_search(company, max_articles)
            
            save_to_cache(cache_key, articles)
            return articles
        except Exception as e:
            log_error(e, "News extraction failed")
            return []

    def _newsapi_search(self, company: str, max_articles: int) -> List[Dict[str, Any]]:
        """Use NewsAPI for reliable news fetching"""
        try:
            url = f"https://newsapi.org/v2/everything?q={company}&apiKey={config.NEWSAPI_KEY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            articles = []
            for item in response.json().get('articles', [])[:max_articles]:
                article = self._process_newsapi_item(item)
                if article:
                    articles.append(article)
            return articles
        except Exception as e:
            log_error(e, "NewsAPI search failed")
            return []

    def _process_newsapi_item(self, item: Dict) -> Optional[Dict]:
        """Process NewsAPI response item"""
        try:
            return {
                "title": item.get('title', ''),
                "url": item.get('url', ''),
                "content": clean_text(item.get('content', '')),
                "summary": clean_text(item.get('description', '')),
                "source": item.get('source', {}).get('name', ''),
                "publish_date": item.get('publishedAt', ''),
            }
        except Exception as e:
            log_error(e, "NewsAPI item processing failed")
            return None

    def _google_news_rss_search(self, company: str, max_articles: int) -> List[Dict[str, Any]]:
        """Fallback to Google News RSS feed"""
        try:
            rss_url = f"https://news.google.com/rss/search?q={company}"
            response = requests.get(rss_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'xml')
            
            articles = []
            for item in soup.find_all('item')[:max_articles]:
                article = self._process_rss_item(item)
                if article:
                    articles.append(article)
            return articles
        except Exception as e:
            log_error(e, "Google News RSS search failed")
            return []

    def _process_rss_item(self, item) -> Optional[Dict]:
        """Process RSS feed item"""
        try:
            url = item.link.text.split('url=')[-1] if 'url=' in item.link.text else item.link.text
            return {
                "title": item.title.text,
                "url": url,
                "content": clean_text(item.description.text),
                "summary": clean_text(item.description.text)[:200] + "...",
                "source": item.source.text if item.source else "Unknown",
                "publish_date": item.pubDate.text if item.pubDate else "",
            }
        except Exception as e:
            log_error(e, "RSS item processing failed")
            return None

    def _extract_article_content(self, url: str) -> Optional[str]:
        """Improved article content extraction"""
        try:
            article = Article(url, config=self.news_config)
            article.download()
            article.parse()
            return clean_text(article.text)
        except Exception as e:
            log_error(e, f"Content extraction failed for {url}")
            return None