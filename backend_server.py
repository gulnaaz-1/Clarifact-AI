import uvicorn
from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import time
import random
import requests
import logging
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup
import re
from collections import Counter

# Import actual ML models
from models import (
    get_fake_news_model, 
    get_sentiment_model,
    get_nli_model,
    get_embed_model,
    get_spacy_model,
    check_models_available
)
from fetchers import fetch_all

# --- CONFIGURATION ---
# Set to FALSE to load actual HuggingFace models (Requires ~4GB RAM + PyTorch)
# Set to TRUE to use heuristic logic for testing without downloading 2GB+ of models
USE_MOCK_MODELS = False  # Changed to use actual models 

REDDIT_RSS_FEEDS = [
    "https://www.reddit.com/r/news/.rss",
    "https://www.reddit.com/r/worldnews/.rss",
    "https://www.reddit.com/r/india/.rss",
    "https://www.reddit.com/r/politics/.rss"
]
GOOGLE_NEWS_RSS = "https://news.google.com/rss"

# Model info to show on frontend
MODELS_IN_USE = {
    "fake_news_detection": "jy46604790/Fake-News-Bert-Detect",
    "sentiment_analysis": "cardiffnlp/twitter-roberta-base-sentiment",
    "nli_contradiction": "roberta-large-mnli",
    "embeddings": "all-MiniLM-L6-v2",
    "ner_entity": "spacy en_core_web_sm"
}

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ViralWarnSystem")

# --- DATA MODELS ---

class AnalyzeRequest(BaseModel):
    text: str
    title: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None

class RiskComponents(BaseModel):
    fake_news_score: float
    contradiction_score: float
    sensationalism_score: float
    source_credibility: float
    virality_score: float

class AnalysisResponse(BaseModel):
    risk_score: float
    risk_level: str
    components: RiskComponents
    claims: List[str]
    evidence: List[str]
    geolocation: str
    reasoning: str
    timestamp: str
    models_used: Dict[str, str]  # Added: show which models were used

class NewsItem(BaseModel):
    id: str
    title: str
    summary: str
    source: str
    url: str
    image_url: Optional[str]
    risk_score: float
    geolocation: str
    timestamp: str
    confidence: float = 0.0  # Added: model confidence

# --- ML & UTILS ENGINE ---

class MLEngine:
    def __init__(self, mock_mode=False):
        self.mock_mode = mock_mode
        self.cached_feed = []
        self.last_fetch = 0
        
        if not self.mock_mode:
            logger.info("Loading ML Models (this may take a while)...")
            try:
                self.fake_news_clf = get_fake_news_model()
                self.sentiment_clf = get_sentiment_model()
                self.nli_clf = get_nli_model()
                self.embed_model = get_embed_model()
                self.nlp = get_spacy_model()
                logger.info("✓ All ML models loaded successfully!")
            except Exception as e:
                logger.error(f"Failed to load models: {e}")
                logger.warning("Falling back to mock mode")
                self.mock_mode = True
        else:
            logger.info("Using MOCK models for testing")
            self.fake_news_clf = None
            self.sentiment_clf = None
            self.nli_clf = None
            self.embed_model = None
            self.nlp = None

    def extract_geo(self, text: str) -> str:
        """Extracts GPE (Geopolitical Entity) from text using spaCy NER."""
        if self.mock_mode or not self.nlp:
            # Mock extraction - look for common country patterns
            countries = ["India", "USA", "UK", "China", "Russia", "Europe", "Asia", "Africa"]
            for country in countries:
                if country.lower() in text.lower():
                    return country
            return "Global"
        
        try:
            doc = self.nlp(text[:500])
            gpes = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
            if gpes:
                return gpes[0]
        except Exception as e:
            logger.debug(f"Error extracting geo: {e}")
        
        return "Global"

    def extract_claims(self, text: str) -> List[str]:
        """Extracts key claims from text."""
        if self.mock_mode or not self.nlp:
            sentences = [s.strip() for s in text.split('.') if len(s) > 20]
            return sentences[:3]
        
        try:
            doc = self.nlp(text[:1000])
            claims = [sent.text.strip() for sent in doc.sents if len(sent.text) > 10]
            return claims[:5]
        except Exception as e:
            logger.debug(f"Error extracting claims: {e}")
            return [text[:100]]

    def analyze_text(self, text: str, source: str = "") -> Dict:
        """Main scoring logic with real ML models."""
        if self.mock_mode:
            # Mock mode fallback
            risk = 0.1
            trigger_words = ['shocking', 'died', 'plot', 'virus', 'secret', 'banned', 'crisis']
            sensationalism = sum(1 for w in trigger_words if w in text.lower()) * 0.15
            
            if "reddit" in source.lower():
                risk += 0.1
            
            risk += sensationalism
            risk = min(0.95, risk)
            
            return {
                "risk_score": round(risk, 2),
                "fake_news_score": round(risk * 0.8, 2),
                "sensationalism": round(min(0.9, sensationalism + 0.1), 2),
                "confidence": 0.5,
                "reasoning": "Detected high usage of emotive language." if risk > 0.5 else "Content appears neutral."
            }

        # === REAL ML INFERENCE ===
        try:
            # 1. Fake News Detection
            fn_input = text[:512]
            fn_result = self.fake_news_clf(fn_input)[0]
            fn_label = fn_result['label'].upper()
            fn_score = fn_result['score']
            
            # If labeled as "REAL", invert score (lower is better)
            # If labeled as "FAKE", use score as is
            fake_news_score = fn_score if "FAKE" in fn_label else (1 - fn_score)
            
            # 2. Sentiment Analysis (negative sentiment = higher sensationalism risk)
            sent_result = self.sentiment_clf(fn_input)[0]
            sent_label = sent_result['label'].upper()
            sent_score = sent_result['score']
            
            # LABEL_0 = Negative, LABEL_1 = Neutral, LABEL_2 = Positive
            # Higher sensationalism if negative or strongly positive
            if "LABEL_0" in sent_label or "NEGATIVE" in sent_label:
                sensationalism_score = sent_score
            elif "LABEL_2" in sent_label or "POSITIVE" in sent_label:
                sensationalism_score = sent_score * 0.6  # Positive isn't always sensational
            else:
                sensationalism_score = 0.2  # Neutral is low risk
            
            # 3. Source credibility heuristic
            source_cred = 0.5
            trusted_sources = ["BBC", "Reuters", "AP News", "Guardian", "NPR"]
            questionable_sources = ["InfoWars", "Breitbart", "Natural News"]
            
            for trusted in trusted_sources:
                if trusted.lower() in source.lower():
                    source_cred = 0.85
                    break
            
            for questionable in questionable_sources:
                if questionable.lower() in source.lower():
                    source_cred = 0.3
                    break
            
            # 4. Compute final risk score
            # Weights: fake news (40%), sensationalism (35%), source credibility (25%)
            risk_score = (
                fake_news_score * 0.40 +
                sensationalism_score * 0.35 +
                (1 - source_cred) * 0.25
            )
            
            risk_score = min(1.0, max(0.0, risk_score))
            
            reasoning = (
                f"Fake News Risk: {fake_news_score:.2f} (Model: {fn_label}), "
                f"Sensationalism: {sensationalism_score:.2f}, "
                f"Source Credibility: {source_cred:.2f}"
            )
            
            return {
                "risk_score": round(risk_score, 3),
                "fake_news_score": round(fake_news_score, 3),
                "sensationalism": round(sensationalism_score, 3),
                "source_credibility": round(source_cred, 3),
                "confidence": round(fn_score, 3),
                "reasoning": reasoning
            }
        
        except Exception as e:
            logger.error(f"Error in model inference: {e}")
            logger.warning("Falling back to heuristic analysis")
            # Fallback heuristic
            risk = 0.3
            if any(w in text.lower() for w in ['shocking', 'breaking', 'viral']):
                risk += 0.2
            return {
                "risk_score": min(0.95, risk),
                "fake_news_score": 0.5,
                "sensationalism": 0.3,
                "source_credibility": 0.5,
                "confidence": 0.0,
                "reasoning": "Using fallback heuristic analysis"
            }

    def clean_html(self, html_content):
        """Remove HTML tags from content."""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text()

    async def fetch_feeds(self):
        """Fetches from multiple real news sources and runs analysis."""
        current_time = time.time()
        
        # Cache for 5 minutes
        if current_time - self.last_fetch < 300 and self.cached_feed:
            logger.info("Using cached feed")
            return self.cached_feed

        logger.info("Fetching real news from multiple sources...")
        news_items = []
        
        try:
            # Fetch from all sources using the enhanced fetchers
            all_items = fetch_all(include_questionable=True)
            
            for item in all_items[:30]:  # Process top 30 items
                try:
                    text_content = f"{item['title']} {item['text']}"
                    
                    # Analyze content with real models
                    metrics = self.analyze_text(text_content, item['source'])
                    geo = self.extract_geo(text_content)
                    
                    # Use image if available, otherwise fallback
                    img_url = item.get('image_url') or f"https://source.unsplash.com/random/400x300?sig={random.randint(1,1000)}"
                    
                    news_item = {
                        "id": item['url'] or item['id'],
                        "title": item['title'][:100],
                        "summary": item['text'][:200],
                        "source": item['source'],
                        "url": item['url'],
                        "image_url": img_url,
                        "risk_score": metrics["risk_score"],
                        "geolocation": geo,
                        "timestamp": datetime.now().strftime("%H:%M"),
                        "confidence": metrics.get("confidence", 0.0)
                    }
                    news_items.append(news_item)
                    
                except Exception as e:
                    logger.debug(f"Error processing item: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error fetching feeds: {e}")
            return []

        # Sort by risk score (descending)
        news_items.sort(key=lambda x: x['risk_score'], reverse=True)
        
        self.cached_feed = news_items
        self.last_fetch = current_time
        logger.info(f"Processed {len(news_items)} news items")
        
        return news_items

# --- INIT APP ---

app = FastAPI(title="ViralWarn Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ml_engine = MLEngine(mock_mode=USE_MOCK_MODELS)

# --- ROUTES ---

@app.get("/")
def health_check():
    return {
        "status": "online",
        "mode": "MOCK" if USE_MOCK_MODELS else "PRODUCTION",
        "models": MODELS_IN_USE
    }

@app.get("/models")
def get_models_info():
    """Return information about active ML models."""
    return {
        "models": MODELS_IN_USE,
        "mode": "MOCK" if USE_MOCK_MODELS else "PRODUCTION",
        "description": {
            "fake_news_detection": "BERT model trained to detect fake news",
            "sentiment_analysis": "RoBERTa model for sentiment classification",
            "nli_contradiction": "RoBERTa model for natural language inference",
            "embeddings": "Sentence transformer for semantic similarity",
            "ner_entity": "SpaCy NER model for named entity recognition"
        }
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalyzeRequest):
    # 1. Extract Info
    claims = ml_engine.extract_claims(request.text)
    geo = ml_engine.extract_geo(request.text)
    
    # 2. Compute Risk
    metrics = ml_engine.analyze_text(request.text)
    
    # 3. Determine Level
    score = metrics["risk_score"]
    level = "LOW"
    if score > 0.3: level = "MEDIUM"
    if score > 0.6: level = "HIGH"
    if score > 0.8: level = "CRITICAL"

    return {
        "risk_score": score,
        "risk_level": level,
        "components": {
            "fake_news_score": metrics["fake_news_score"],
            "contradiction_score": 0.0,
            "sensationalism_score": metrics.get("sensationalism", 0.0),
            "source_credibility": metrics.get("source_credibility", 0.5),
            "virality_score": 0.0
        },
        "claims": claims,
        "evidence": [],
        "geolocation": geo,
        "reasoning": metrics["reasoning"],
        "timestamp": datetime.now().isoformat(),
        "models_used": MODELS_IN_USE
    }

@app.get("/feed", response_model=List[NewsItem])
async def get_feed():
    return await ml_engine.fetch_feeds()

@app.get("/heatmap")
async def get_heatmap():
    """Aggregates risk scores by Geolocation from current feed."""
    items = await ml_engine.fetch_feeds()
    
    geo_risk = {}
    geo_counts = {}
    
    for item in items:
        geo = item['geolocation']
        if geo == "Global": continue
        
        if geo not in geo_risk:
            geo_risk[geo] = 0.0
            geo_counts[geo] = 0
        
        geo_risk[geo] += item['risk_score']
        geo_counts[geo] += 1
        
    # Calculate average
    result = {}
    for geo in geo_risk:
        result[geo] = round(geo_risk[geo] / geo_counts[geo], 2)
        
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)