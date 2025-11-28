# ML Models Integration - Clarifact-AI

## Overview
This document describes the integration of real ML models and real-time news sources into the Clarifact-AI system for comprehensive fake news detection and analysis.

---

## 🚀 What's New

### 1. **Real ML Models Integrated**

The system now uses **5 state-of-the-art transformer models** for comprehensive content analysis:

#### Fake News Detection
- **Model**: `jy46604790/Fake-News-Bert-Detect`
- **Purpose**: Primary classifier for detecting fake news content
- **Output**: Binary classification (REAL/FAKE) with confidence score
- **Architecture**: BERT-based fine-tuned on fake news datasets

#### Sentiment Analysis
- **Model**: `cardiffnlp/twitter-roberta-base-sentiment`
- **Purpose**: Detects sentiment polarity and emotional manipulation
- **Output**: Three labels (NEGATIVE, NEUTRAL, POSITIVE) with scores
- **Use Case**: Identifies sensationalism and emotive language

#### Natural Language Inference (NLI)
- **Model**: `roberta-large-mnli`
- **Purpose**: Detects contradictions between claims and evidence
- **Output**: Entailment/Contradiction/Neutral classification
- **Use Case**: Validates factual consistency

#### Sentence Embeddings
- **Model**: `all-MiniLM-L6-v2`
- **Purpose**: Semantic similarity analysis
- **Output**: 384-dimensional embeddings
- **Use Case**: Fallback contradiction detection via cosine similarity

#### Named Entity Recognition (NER)
- **Model**: `spacy en_core_web_sm`
- **Purpose**: Extracts locations, people, organizations
- **Output**: Entity types and boundaries
- **Use Case**: Geolocation extraction, fact extraction

---

### 2. **Real-Time News Sources**

The system now fetches from **multiple real news sources**:

#### Reputed News Sources (Trusted)
- BBC News
- Reuters
- AP News
- The Guardian
- NPR

#### Entertainment & Trending
- TMZ
- Reddit (News, World News, India)
- Google News

#### Questionable/Sensational Sources (For Comparison)
- Breitbart
- InfoWars
- Natural News

#### API Integration
- **NewsAPI** support (requires API key in environment variable `NEWSAPI_KEY`)

---

### 3. **Enhanced Risk Scoring Algorithm**

The new scoring combines multiple ML models with weighted components:

```
Risk Score = (
    0.35 × Fake_News_Score +
    0.25 × Sensationalism_Score +
    0.20 × Contradiction_Score +
    0.15 × (1 - Source_Credibility) +
    0.05 × Virality_Score
)
```

#### Components:
- **Fake News Score** (0-1): Output from BERT fake news detector
- **Sensationalism Score** (0-1): Combination of keyword matching + sentiment analysis
- **Contradiction Score** (0-1): NLI model detecting claim contradictions
- **Source Credibility** (0-1): Domain reputation-based scoring
- **Virality Score** (0-1): Heuristic based on engagement metrics

---

## 📁 Files Modified

### Backend Files

#### `models.py` (NEW STRUCTURE)
- **Lazy-loaded model initialization** to conserve memory
- Centralized model loading with error handling
- Functions to load individual models on-demand
- Models loaded only when needed, kept in global cache
- Includes `unload_all_models()` for memory cleanup

```python
from models import (
    get_fake_news_model,
    get_sentiment_model,
    get_nli_model,
    get_embed_model,
    get_spacy_model
)
```

#### `fetchers.py` (ENHANCED)
- **Multiple RSS feed sources** (reputed, entertainment, questionable)
- `fetch_reputed_news()` - BBC, Reuters, Guardian, etc.
- `fetch_questionable_news()` - Breitbart, InfoWars, etc.
- `fetch_entertainment_news()` - TMZ, Reddit
- `fetch_via_newsapi()` - NewsAPI integration
- Comprehensive error handling and logging
- Deduplication by URL

#### `scorer.py` (COMPLETE REWRITE)
- Uses **real ML models** instead of heuristics
- `sensational_score()` - Combines keywords + sentiment model
- `fake_news_score()` - BERT classification
- `contradiction_score()` - NLI-based validation
- `extract_claims()` - Spacy NER for fact extraction
- `compute_risk()` - Comprehensive risk calculation

#### `backend_server.py` (UPDATED)
- Set `USE_MOCK_MODELS = False` to enable real models
- Enhanced `MLEngine` class with real model inference
- New `/models` endpoint showing active models
- Updated `AnalysisResponse` to include `models_used`
- Better error handling with fallback to heuristics
- Fetch from real news sources via `fetch_all()`

#### `config.py` (EXISTING)
- Already contains news feed URLs
- Supports `USE_HEAVY_MODELS` flag

### Frontend Files

#### `clarifact/app/page.tsx` (ENHANCED)
- New `/models` endpoint integration
- Display active ML models in analyze page
- Show model confidence scores
- Component-level model info display
- News feed confidence percentages
- Enhanced model reasoning display

#### `requirements.txt` (UPDATED)
Added dependencies:
```
torch>=2.0.0
torchaudio
torchvision
transformers>=4.35.0
sentence-transformers>=2.2.0
spacy>=3.7.0
aiohttp
pydantic-settings
PyJWT
newsapi>=1.0
```

---

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Optional: NewsAPI Setup
Get a free API key from [newsapi.org](https://newsapi.org) and add to environment:
```bash
export NEWSAPI_KEY=your_key_here
```

### 3. Run Backend
```bash
cd c:\Users\ABHINAV\Desktop\Prog\Projects\Clarifact-AI
python backend_server.py
# Backend runs on http://localhost:8000
```

### 4. Run Frontend
```bash
cd clarifact
npm run dev
# Frontend runs on http://localhost:3000
```

---

## 📊 API Endpoints

### Health Check
```
GET /
Response: { status, mode, models }
```

### Analyze Content
```
POST /analyze
Body: { text, title?, url?, image_url? }
Response: AnalysisResponse with risk_score, components, models_used
```

### Get Feed
```
GET /feed
Response: List[NewsItem] with risk scores
```

### Model Information
```
GET /models
Response: { models, mode, descriptions }
```

### Heatmap (Geo Risk Distribution)
```
GET /heatmap
Response: { location: risk_score, ... }
```

---

## 🎯 Risk Score Interpretation

| Score | Level | Interpretation |
|-------|-------|-----------------|
| 0.0 - 0.3 | LOW | Content appears reliable |
| 0.3 - 0.6 | MEDIUM | Some risk indicators detected |
| 0.6 - 0.8 | HIGH | Significant fake news patterns |
| 0.8 - 1.0 | CRITICAL | Very likely misinformation |

---

## 💡 Model Features

### Fake News Detection
- Detects fabricated claims, false quotations
- Identifies out-of-context usage
- Scores misleading headlines

### Sensationalism Detection
- Identifies emotive language
- Detects clickbait patterns
- Scores urgency language (breaking, urgent, alert)

### Contradiction Detection
- Uses NLI to find logical inconsistencies
- Compares claims with known facts
- Identifies conflicting statements

### Source Credibility
- Domain reputation scoring
- Trusted vs untrusted source classification
- Publisher credibility assessment

---

## 🔍 Example Usage

### Python Backend Analysis
```python
from backend_server import ml_engine

text = "Breaking: Scientists discover cure for everything!"
result = ml_engine.analyze_text(text, source="Unknown")
print(result)
# Output: 
# {
#   'risk_score': 0.87,
#   'fake_news_score': 0.92,
#   'sensationalism': 0.85,
#   'confidence': 0.91,
#   'reasoning': '...'
# }
```

### Frontend API Call
```javascript
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    text: "Suspicious content here...",
    title: "Article title",
    url: "https://example.com"
  })
});

const analysis = await response.json();
console.log(analysis.models_used); // See which models analyzed content
```

---

## ⚙️ Configuration

### Model Lazy Loading
Models are loaded only when first needed, reducing startup time:
- First call to analysis triggers model loading (~30-60s)
- Models stay in memory for subsequent requests
- Call `unload_all_models()` to free memory

### Fallback Behavior
If real models fail to load or error:
- System gracefully falls back to heuristic analysis
- Shows confidence = 0.0 for fallback scores
- Still returns valid risk assessments

### Performance Optimization
- Text input truncated to 512 tokens for models (standard limit)
- Feed processing limited to 30 items per fetch
- 5-minute caching of feed results
- Async operations for non-blocking requests

---

## 🚨 Important Notes

### Memory Requirements
- All models loaded: ~4-6GB RAM
- First load takes 30-60 seconds
- Requires GPU support (auto-detects)

### API Rate Limits
- NewsAPI: Free tier has daily limits (~100 requests/day)
- Wikipedia search: 3-second timeout per query
- RSS feeds: No rate limits (public feeds)

### Production Considerations
- Use environment variables for API keys
- Implement request validation
- Add authentication for API endpoints
- Consider model quantization for smaller deployments
- Monitor memory usage in production

---

## 🔄 Model Update Path

To use different models, modify `models.py`:

```python
FAKE_NEWS_MODEL = "your-new-fake-news-model"
SENTIMENT_MODEL = "your-new-sentiment-model"
# etc.
```

Available model repositories:
- [Hugging Face Models](https://huggingface.co/models)
- [Real News Detection Models](https://huggingface.co/models?search=fake%20news)
- [Sentiment Models](https://huggingface.co/models?pipeline_tag=text-classification)

---

## 📝 Logging & Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Common issues:
1. **Model download fails**: Check internet connection, disk space
2. **GPU not detected**: Ensure PyTorch GPU support is installed
3. **API timeouts**: Increase timeout values in config
4. **Memory errors**: Reduce batch size or use smaller models

---

## 🎓 Model Information

Each model trained on:
- **Fake News BERT**: Millions of labeled articles
- **Sentiment RoBERTa**: Twitter sentiment corpus
- **NLI RoBERTa**: MNLI multi-genre dataset
- **Sentence Transformers**: NLI + STS datasets

All models are publicly available under open licenses (Apache 2.0, MIT).

---

## 📞 Support

For issues with:
- **Models**: Check Hugging Face documentation
- **Data Sources**: Verify RSS feeds are accessible
- **Frontend**: Check browser console for API errors
- **Backend**: Check server logs for detailed error messages

---

**Last Updated**: November 2024
**Version**: 2.0.0 (ML Models Integration)
