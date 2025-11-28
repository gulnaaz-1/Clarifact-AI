# fetchers.py - fetch trending items from multiple reputed and questionable sources
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import logging
import os
from config import REDDIT_RSS_FEEDS, GOOGLE_NEWS_RSS, NITTER_SEARCH_URL

logger = logging.getLogger("ViralWarnSystem")

# === Real News Sources (Reputed) ===
REPUTED_RSS_FEEDS = [
    {"name": "BBC News", "url": "http://feeds.bbc.co.uk/news/rss.xml"},
    {"name": "Reuters", "url": "https://www.reutersagency.com/feed/?taxonomy=best-topics&output=rss"},
    {"name": "AP News", "url": "https://apnews.com/apf-services/v2/homepage?format=rss"},
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
    {"name": "NPR", "url": "https://feeds.npr.org/1001/rss.xml"},
]

# === Questionable/Sensational News Sources ===
QUESTIONABLE_RSS_FEEDS = [
    {"name": "Breitbart", "url": "https://feeds.breitbart.com/breitbart-feed/"},
    {"name": "InfoWars (labeled)", "url": "https://www.infowars.com/feed/"},
    {"name": "Natural News (labeled)", "url": "https://www.naturalnews.com/?feed=rss2"},
]

# === Entertainment & Trending ===
ENTERTAINMENT_FEEDS = [
    {"name": "TMZ", "url": "https://www.tmz.com/rss.xml"},
    {"name": "Reddit News", "url": "https://www.reddit.com/r/news/.rss"},
    {"name": "Reddit World News", "url": "https://www.reddit.com/r/worldnews/.rss"},
]

# === India-Specific News Sources ===
INDIA_NEWS_FEEDS = [
    {"name": "The Hindu", "url": "https://www.thehindu.com/news/national/?service=rss"},
    {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"},
    {"name": "Indian Express", "url": "https://indianexpress.com/feed/"},
    {"name": "NDTV India", "url": "https://feeds.ndtv.com/ndtv/india.xml"},
    {"name": "India Today", "url": "https://www.indiatoday.in/feeds/latest.xml"},
    {"name": "Deccan Herald", "url": "https://www.deccanherald.com/rss/india.xml"},
    {"name": "The Wire", "url": "https://thewire.in/feed/"},
    {"name": "Scroll.in", "url": "https://scroll.in/feed"},
]

def parse_feed_entry(e, source_name: str = "Unknown") -> Dict:
    """Parse a single RSS feed entry into our standard format."""
    title = e.get('title', '')
    link = e.get('link', '') or getattr(e, 'link', '')
    summary = e.get('summary', '') or e.get('description', '') or getattr(e, 'summary', '')
    
    # Clean HTML from summary
    if summary:
        summary = BeautifulSoup(summary, 'html.parser').get_text()
    
    published = e.get('published', '') or e.get('updated', '') or getattr(e, 'published', '')
    
    return {
        'id': link or title,
        'title': title,
        'text': summary[:500],  # Limit to 500 chars
        'url': link,
        'source': source_name,
        'published': published,
        'timestamp': datetime.now().isoformat()
    }

def fetch_rss_feed(feed_url: str, source_name: str, limit: int = 15) -> List[Dict]:
    """Fetch items from a single RSS feed."""
    items = []
    try:
        logger.info(f"Fetching from {source_name} ({feed_url})")
        d = feedparser.parse(feed_url)
        
        if d.bozo:  # Feed parsing had issues but may still have data
            logger.warning(f"Feed parsing issues for {source_name}: {d.bozo_exception}")
        
        if not d.entries:
            logger.warning(f"No entries found in {source_name}")
            return items
        
        for e in d.entries[:limit]:
            try:
                item = parse_feed_entry(e, source_name)
                if item['title'] and item['url']:  # Only add if we have title and URL
                    items.append(item)
            except Exception as entry_err:
                logger.debug(f"Error parsing entry from {source_name}: {entry_err}")
                continue
        
        logger.info(f"Successfully fetched {len(items)} items from {source_name}")
    except Exception as e:
        logger.error(f"Error fetching {source_name}: {e}")
    
    return items

def fetch_reputed_news(limit: int = 20) -> List[Dict]:
    """Fetch from reputed news sources."""
    items = []
    for feed_info in REPUTED_RSS_FEEDS:
        feed_items = fetch_rss_feed(feed_info["url"], feed_info["name"], limit=limit)
        items.extend(feed_items)
    return items

def fetch_questionable_news(limit: int = 20) -> List[Dict]:
    """Fetch from questionable/sensational news sources (for comparison)."""
    items = []
    for feed_info in QUESTIONABLE_RSS_FEEDS:
        feed_items = fetch_rss_feed(feed_info["url"], feed_info["name"], limit=limit)
        items.extend(feed_items)
    return items

def fetch_entertainment_news(limit: int = 15) -> List[Dict]:
    """Fetch entertainment and trending content."""
    items = []
    for feed_info in ENTERTAINMENT_FEEDS:
        feed_items = fetch_rss_feed(feed_info["url"], feed_info["name"], limit=limit)
        items.extend(feed_items)
    return items

def fetch_india_news(limit: int = 20) -> List[Dict]:
    """Fetch India-specific news from reputed Indian sources."""
    items = []
    for feed_info in INDIA_NEWS_FEEDS:
        feed_items = fetch_rss_feed(feed_info["url"], feed_info["name"], limit=limit)
        items.extend(feed_items)
    return items

def fetch_via_newsapi(api_key: str = None, limit: int = 20) -> List[Dict]:
    """Fetch news via NewsAPI (requires API key)."""
    items = []
    if not api_key:
        api_key = os.getenv("NEWSAPI_KEY")
    
    if not api_key:
        logger.warning("NewsAPI key not found. Skipping NewsAPI fetch.")
        return items
    
    try:
        # Fetch from multiple sources
        sources = ["bbc-news", "cnn", "reuters", "the-guardian", "breitbart"]
        for source in sources:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "sources": source,
                "pageSize": limit,
                "apiKey": api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get("articles", []):
                    item = {
                        'id': article.get('url', ''),
                        'title': article.get('title', ''),
                        'text': article.get('description', '')[:500],
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'NewsAPI'),
                        'published': article.get('publishedAt', ''),
                        'timestamp': datetime.now().isoformat(),
                        'image_url': article.get('urlToImage', '')
                    }
                    items.append(item)
            else:
                logger.warning(f"NewsAPI error for {source}: {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching from NewsAPI: {e}")
    
    return items

def fetch_all(include_questionable: bool = True) -> List[Dict]:
    """Fetch from all sources and deduplicate."""
    results = []
    
    # Fetch from all sources
    results.extend(fetch_reputed_news(limit=12))
    results.extend(fetch_entertainment_news(limit=10))
    results.extend(fetch_india_news(limit=15))  # India-specific news
    
    if include_questionable:
        results.extend(fetch_questionable_news(limit=10))
    
    # Try NewsAPI if available
    results.extend(fetch_via_newsapi(limit=15))
    
    # Deduplicate by URL
    seen = set()
    uniq = []
    for r in results:
        if r['url'] and r['url'] not in seen:
            uniq.append(r)
            seen.add(r['url'])
        elif not r['url'] and r['id'] not in seen:
            uniq.append(r)
            seen.add(r['id'])
    
    logger.info(f"Total unique items fetched: {len(uniq)}")
    return uniq
