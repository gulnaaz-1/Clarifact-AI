# Clarifact-AI  
### Real-time Misinformation Analysis, Scoring & Intelligence System

Clarifact-AI is an experimental end-to-end system designed to monitor live news streams, analyze content credibility, and highlight early misinformation signals. It combines:

- A **Python/FastAPI backend** for ML-based analysis  
- A **Node.js (React/TypeScript) frontend** for real-time monitoring  
- A **hybrid ML scoring engine** using multiple Transformer models  
- A **news ingestion pipeline** connected to reputable, questionable, and trending sources  

Clarifact-AI is not a fact-checking engine. It provides **early indicators** of content that may require manual review.

.
├── clarifact/                 # UI of the System 
│
├── utils/                     # Utility scripts (geo lookup, helpers, formatters, shared tools)
│
├── config.py                  # Central configuration file (thresholds, feed lists, intervals, toggles)
├── fetchers.py                # News ingestion layer (RSS, Reddit, NewsAPI, questionable + reputed sources)
├── models.py                  # Lazy-loading model manager (BERT, RoBERTa, MiniLM, spaCy)
├── scorer.py                  # Main misinformation scoring engine (claims, evidence, NLI, risk computation)
├── store.py                   # In-memory event store (recent feed items, geo-topic counters)
│
├── backend_server.py          # Full FastAPI backend (API endpoints: /analyze, /feed, /models, /heatmap)
├── app.py                     # Application runner (UI or alternate backend entrypoint)
├── app_b.py                   # Minimal FastAPI API for lightweight deployments (/analyze only)
│
├── setup_ml_models.py         # Setup script (model downloads, environment checks, spaCy installation)
├── requirements.txt           # Python dependencies for backend + ML stack
├── .env.example               # Example environment variable configuration (API keys, settings)
│
├── documentation/             # All architecture, integration, and visualization docs
│   ├── ARCHITECTURE.md
│   ├── ML_MODELS_INTEGRATION.md
│   ├── INTEGRATION_SUMMARY.md
│   ├── IMPLEMENTATION_CHECKLIST.md
│   ├── GLOBE_VISUALIZATION_GUIDE.md
│   ├── GLOBE_HEATMAP_UPDATE.md
│   ├── HEATMAP_INDIA_UPDATE.md
│   ├── QUICK_REFERENCE.md
│   └── START_HERE.txt
│
└── clarifact-frontend/        # Node.js/React frontend (dashboard, feed view, analyze UI, heatmaps)
    ├── package.json
    ├── src/
    ├── public/
    └── README.md

---

##  Key Capabilities
- Real-time ingestion of 30+ news feeds  
- Hybrid risk scoring (Fake News BERT, RoBERTa Sentiment, NLI, MiniLM embeddings, spaCy NER)  
- Wikipedia-based evidence lookup  
- Contradiction detection  
- Geo-topic intelligence & heatmap aggregation  
- Node.js-based monitoring dashboard  
- Lazy-loaded models (memory efficient)  
- Full FastAPI backend with multiple endpoints  

---

## System Architecture

### **Frontend (Node.js / Python / TypeScript)**  
- Dashboard with risk feed, trends, geo-topic stats  
- Analyze view for custom text evaluation  
- Heatmap view  
- Uses HTTP requests to FastAPI backend  

### **Backend (FastAPI / Python)**  
- `/analyze` – analyze text and return ML evaluation  
- `/feed` – return the scored feed  
- `/heatmap` – aggregated geo-topic risk  
- `/models` – status of ML models  
- Uses lazy loading for heavy models  

### **ML Engine Components**

| Component | Model | Purpose |
|----------|--------|---------|
| Fake News Detection | `jy46604790/Fake-News-Bert-Detect` | Real/Fake scoring |
| Sentiment/Sensationalism | `cardiffnlp/twitter-roberta-*` | Emotional tone |
| NLI Contradiction | `roberta-large-mnli` | Detect contradictions |
| Embedding Similarity | `all-MiniLM-L6-v2` | Semantic similarity |
| Named Entity Recognition | `spaCy en_core_web_sm` | GPE/ORG/LOC extraction |

---

##  News Ingestion Pipeline

Sources include:

- **Reputed:** BBC, Reuters, AP, Guardian, NPR  
- **India-specific:** Times of India, Indian Express, NDTV, Hindu  
- **Trending:** Reddit, Google News RSS  
- **Questionable:** InfoWars, NaturalNews, Breitbart  
- **Optional:** NewsAPI  

Content is parsed, cleaned, deduplicated, timestamped, and stored in memory.

---

##  Risk Scoring Model

```
Risk Score =
  0.35 × Fake News BERT
+ 0.25 × Sentiment/Sensationalism
+ 0.20 × NLI Contradiction
+ 0.15 × (1 - Source Credibility)
+ 0.05 × Virality Heuristic
```

### 🚦 Risk Levels

| Score | Meaning |
|--------|---------|
| 0.0–0.3 | 🟢 Low |
| 0.3–0.6 | 🟡 Medium |
| 0.6–0.8 | 🟠 High |
| 0.8–1.0 | 🔴 Critical |

---

##  Lazy Loading Lifecycle

- First model request → download + cache  
- Subsequent requests → near-instant inference  
- Fallback to heuristic mode if a model fails  

---

## Performance Characteristics

- Model load (initial): **30–60 sec**  
- Inference: **1–3 sec** per request  
- Feed scoring: **5–10 sec**  
- Memory footprint: **500MB idle → 4–6GB with all models loaded**  

---

## Project Structure

```
Clarifact-AI/
│── backend_server.py      # FastAPI backend
│── app_b.py               # Minimal API wrapper
│── fetchers.py            # RSS ingestion
│── scorer.py              # Scoring engine
│── models.py              # Lazy model loader
│── store.py               # In-memory storage
│── config.py              # Configuration
│── utils/geo.py           # Geolocation helper
│── setup_ml_models.py     # ML setup script
│── README.md
│
└── clarifact-frontend/    # React/Node.js UI
    │── package.json
    │── src/
    │── public/
    └── ...
```

---

## Installation

### Backend
```bash
pip install -r requirements.txt
python setup_ml_models.py
python backend_server.py
```

Backend runs on:
```
http://localhost:8000
```

### Frontend
```bash
cd clarifact-frontend
npm install
npm run dev
```

Frontend runs on:
```
http://localhost:3000
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Healthcheck |
| `/analyze` | Analyze text |
| `/feed` | Scored feed |
| `/heatmap` | Geo-risk aggregation |
| `/models` | Loaded model info |

---

## Future Work

- Browser extension  
- CLIP-based meme/image misinformation detection  
- Persistent DB for long-term tracking  
- Websocket-based live streaming  
- Multi-language support  

---

## Acknowledgements

Built using: FastAPI, React, HuggingFace Transformers, sentence-transformers, spaCy, feedparser, Wikipedia API.


