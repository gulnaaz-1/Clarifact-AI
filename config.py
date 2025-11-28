# config.py - tweak these for demo speed / thresholds

FETCH_INTERVAL_SECONDS = 60           # how often to poll sources
RISK_THRESHOLD = 0.45                # 0..1 threshold to flag alerts
WIKIPEDIA_TIMEOUT = 3                # seconds for quick evidence fetch
MAX_EVENTS_STORED = 200
USE_HEAVY_MODELS = True              # set False to use fast stubs (demo friendly)
REDDIT_RSS_FEEDS = [
    "https://www.reddit.com/r/news/.rss",
    "https://www.reddit.com/r/worldnews/.rss",
    "https://www.reddit.com/r/india/.rss",
    "https://www.reddit.com/r/politics/.rss"
]
GOOGLE_NEWS_RSS = "https://news.google.com/rss"
# optional Nitter / X scraping: set to None to disable by default
NITTER_SEARCH_URL = 'https://nitter.net/search/rss?q='  # e.g. 'https://nitter.net/search/rss?q='
