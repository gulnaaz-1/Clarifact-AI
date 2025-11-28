# Clarifact-AI Architecture - ML Models Integration

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLARIFACT-AI SYSTEM                            │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (TypeScript/React)                      │
│                                                                          │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐              │
│  │   Dashboard    │  │   Analyze    │  │   Feed View    │              │
│  │  - Live Map    │  │  - Text Box  │  │  - Risk Feed   │              │
│  │  - Statistics  │  │  - Results   │  │  - Heatmap     │              │
│  │  - Trends      │  │  - Models    │  │  - Geo Data    │              │
│  └────────────────┘  └──────────────┘  └────────────────┘              │
│           │                  │                   │                      │
│           └──────────────────┼───────────────────┘                      │
│                              ▼                                          │
│                   ┌─────────────────────┐                              │
│                   │   HTTP Requests     │                              │
│                   │  (FastAPI Client)   │                              │
│                   └─────────────────────┘                              │
└──────────────────────────────────────────────────────────────────────────┘
                              │
                   ┌──────────▼──────────┐
                   │                     │
                   ▼                     ▼
          ┌─────────────────┐   ┌────────────────────┐
          │ /analyze        │   │ /feed              │
          │ /models         │   │ /heatmap           │
          │ /               │   │ /                  │
          └─────────────────┘   └────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                      BACKEND (Python/FastAPI)                           │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                      API LAYER                                │   │
│  │  - AnalysisRequest Handler                                   │   │
│  │  - Feed Endpoint                                             │   │
│  │  - Models Info Endpoint                                      │   │
│  │  - Error Handling & Logging                                  │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│  ┌──────────────────────────▼────────────────────────────────────┐   │
│  │                    ML ENGINE                                  │   │
│  │                                                               │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │ Content Analysis Pipeline                          │    │   │
│  │  │                                                     │    │   │
│  │  │  1. Text Preprocessing & Cleaning                  │    │   │
│  │  │  2. Entity Extraction (spaCy NER)                  │    │   │
│  │  │  3. Parallel Model Inference:                      │    │   │
│  │  │     ├─ Fake News Detection (BERT)                  │    │   │
│  │  │     ├─ Sentiment Analysis (RoBERTa)                │    │   │
│  │  │     ├─ NLI Contradiction (RoBERTa)                 │    │   │
│  │  │     └─ Embeddings (Sentence-Transformers)          │    │   │
│  │  │  4. Risk Score Aggregation (Weighted Sum)          │    │   │
│  │  │  5. Confidence Calculation                         │    │   │
│  │  │  6. Result Formatting                              │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│  ┌──────────────────────────▼────────────────────────────────────┐   │
│  │                   NEWS FETCHING                               │   │
│  │                                                               │   │
│  │  ┌─────────────────┐  ┌──────────────────┐                  │   │
│  │  │ Fetchers.py     │  │ Cache (5 min)    │                  │   │
│  │  │                 │  │                  │                  │   │
│  │  │ ├─ RSS Parsing  │  │ - Feed Results   │                  │   │
│  │  │ ├─ Source Split │  │ - Timestamps     │                  │   │
│  │  │ ├─ Dedup        │  │                  │                  │   │
│  │  │ ├─ Cleaning     │  │                  │                  │   │
│  │  │ └─ Error Handle │  │                  │                  │   │
│  │  └─────────────────┘  └──────────────────┘                  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                         ML MODELS LAYER                                 │
│                         (Lazy Loading)                                  │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │ BERT Fake News   │  │ RoBERTa          │  │ RoBERTa NLI        │  │
│  │ Detector         │  │ Sentiment        │  │ Contradiction      │  │
│  │                  │  │                  │  │                    │  │
│  │ Model:           │  │ Model:           │  │ Model:             │  │
│  │ jy46604790/      │  │ cardiffnlp/      │  │ roberta-large-mnli │  │
│  │ Fake-News-BERT   │  │ twitter-roberta  │  │                    │  │
│  │                  │  │                  │  │                    │  │
│  │ Output:          │  │ Output:          │  │ Output:            │  │
│  │ REAL/FAKE (0-1)  │  │ POS/NEU/NEG      │  │ ENTAIL/CONTRA/etc  │  │
│  └──────────────────┘  └──────────────────┘  └────────────────────┘  │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐                           │
│  │ Sentence         │  │ spaCy NER        │                           │
│  │ Embeddings       │  │ Entity Extract   │                           │
│  │                  │  │                  │                           │
│  │ Model:           │  │ Model:           │                           │
│  │ all-MiniLM-      │  │ en_core_web_sm   │                           │
│  │ L6-v2            │  │                  │                           │
│  │                  │  │ Output:          │                           │
│  │ Output:          │  │ PER/ORG/GPE/LOC  │                           │
│  │ 384-dim vectors  │  │ Named Entities   │                           │
│  └──────────────────┘  └──────────────────┘                           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                      DATA SOURCES LAYER                                 │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │           REPUTED NEWS SOURCES (High Credibility)          │       │
│  │  BBC | Reuters | AP News | Guardian | NPR                  │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │        ENTERTAINMENT & TRENDING (Mixed Credibility)        │       │
│  │  TMZ | Reddit News | Reddit World News | Google News       │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │      QUESTIONABLE SOURCES (Low Credibility Reference)      │       │
│  │  Breitbart | InfoWars | Natural News                       │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │              OPTIONAL API SOURCES                          │       │
│  │  NewsAPI (requires free API key)                          │       │
│  │  Wikipedia (evidence verification)                         │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

```

## Data Flow: Analysis Request

```
User Input (text)
       │
       ▼
┌─────────────────┐
│ API Validation  │ ← Validate request format
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Text Preprocessing  │ ← Truncate to 512 tokens, clean
└────────┬────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│ Parallel Model Inference (Async)                │
│                                                  │
│  ┌──────────────┐  ┌────────────┐  ┌─────────┐ │
│  │ BERT (FAKE)  │  │ Sentiment  │  │ NLI     │ │
│  │ ▼            │  │ ▼          │  │ ▼       │ │
│  │ 0.75         │  │ 0.68       │  │ 0.42    │ │
│  └──────────────┘  └────────────┘  └─────────┘ │
│                                                  │
│  ┌──────────────┐  ┌────────────┐              │
│  │ Embeddings   │  │ NER        │              │
│  │ ▼            │  │ ▼          │              │
│  │ [vector]     │  │ GPE: USA   │              │
│  └──────────────┘  └────────────┘              │
└────────┬─────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Risk Score Calculation     │
│                            │
│ Risk = 0.35×0.75 +         │
│        0.25×0.68 +         │
│        0.20×0.42 +         │
│        0.15×(1-0.8) +      │
│        0.05×0.2            │
│                            │
│ = 0.26 + 0.17 + 0.08 +    │
│   0.03 + 0.01 = 0.55      │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────┐
│ Determine Risk Level   │
│                        │
│ 0.55 → MEDIUM RISK     │
└────────┬───────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Format Response              │
│ - risk_score: 0.55           │
│ - risk_level: "MEDIUM"       │
│ - components: {...}          │
│ - models_used: {...}         │
│ - reasoning: "..."           │
│ - timestamp: "2024-11-28..." │
└────────┬─────────────────────┘
         │
         ▼
    Return to Frontend
```

## Risk Score Components Hierarchy

```
                         RISK SCORE
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    (35%) │            (25%) │            (20%)│
          │                  │                  │
          ▼                  ▼                  ▼
      FAKE NEWS          SENSATIONALISM    CONTRADICTION
      DETECTOR           DETECTION         DETECTION
      (BERT)             (RoBERTa)         (RoBERTa NLI)
          │                  │                  │
    Detects:            Detects:           Detects:
    - False claims    - Emotive language  - Logical
    - Fabrications    - Trigger words      inconsistencies
    - Misleading      - Clickbait         - Claim
      headlines         patterns            contradictions
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                        ┌────┴────┐
                        │          │
                   (15%)│    (5%)  │
                        │          │
                        ▼          ▼
                  SOURCE        VIRALITY
                CREDIBILITY     SCORE
                HEURISTIC       (Heuristic)
                   │                │
              Evaluates:        Estimates:
              - Domain rep     - Engagement
              - Publisher      - Shares
              - History        - Comments
                        │          │
                        └────┬─────┘
                             │
                        ┌────▼──────┐
                        │            │
                        ▼            ▼
                   AGGREGATED    FINAL RISK
                   COMPONENTS    SCORE (0-1)
                   
                        │
                   ┌────┴────┬────────┬────────┐
                   │         │        │        │
                   ▼         ▼        ▼        ▼
                 LOW     MEDIUM    HIGH   CRITICAL
              (0.0-0.3)(0.3-0.6)(0.6-0.8)(0.8-1.0)
```

## Lazy Loading Model Lifecycle

```
START
  │
  ▼
┌─────────────────────────┐
│ Initialize MLEngine     │
│ all models = None       │
│ mock_mode = False       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ First Analysis Request          │
│ get_fake_news_model() called    │
└────────┬────────────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Check Global Cache         │
│ _fake_news_clf is None?    │
└────────┬───────────────────┘
         │
         ├─ YES ─────────────────────────┐
         │                               │
         ▼                               │
    ┌──────────────────────────────┐   │
    │ Download & Load Model        │   │
    │ (30-60 seconds)              │   │
    │ from HuggingFace Hub         │   │
    └─────────┬────────────────────┘   │
              │                         │
              ▼                         │
    ┌──────────────────────────────┐   │
    │ Cache in Global Variable     │   │
    │ _fake_news_clf = model       │   │
    └─────────┬────────────────────┘   │
              │                         │
              └────────────┬────────────┘
                           │
         ┌─ NO ───────────┘
         │
         ▼
    ┌──────────────────────────────┐
    │ Use Cached Model             │
    │ (instant)                    │
    │ _fake_news_clf is not None   │
    └─────────┬────────────────────┘
              │
              ▼
    ┌──────────────────────────────┐
    │ Run Inference                │
    │ output = model(text)         │
    └─────────┬────────────────────┘
              │
              ▼
        Return Result
              │
              ▼
    ┌──────────────────────────────┐
    │ Subsequent Requests          │
    │ All models cached            │
    │ (Fast inference)             │
    └──────────────────────────────┘
```

## Error Handling Flow

```
Request
  │
  ▼
Try to Load Model
  │
  ├─ SUCCESS ──────────────────────────┐
  │                                    │
  │                         Try Inference
  │                            │
  │                    ┌───────┼───────┐
  │                    │               │
  │              SUCCESS         FAILURE
  │                    │               │
  │                    │         Log Error
  │                    │         Fallback to
  │                    │         Heuristic
  │                    │         Set confidence=0
  │                    │               │
  │                    └───────┬───────┘
  │                            │
  └────────────────────────────┼────────────┐
                               │            │
                               ▼            ▼
                          Return Result Return Fallback
                          (High Conf)  (Low Conf)
  │
  └─ FAILURE ──────────────────────────┐
                                       │
                    Log Error Message  │
                    Fall Back to      │
                    Mock Mode         │
                    USE_MOCK_MODELS=True
                                       │
                                       ▼
                                Return Heuristic
                                Analysis Result
```

---

## Key Characteristics

### Performance
- **Model Load Time**: 30-60s (first request only)
- **Inference Time**: 1-3s per request (after loading)
- **Feed Processing**: 5-10s for full feed
- **Caching**: 5-minute feed cache

### Memory
- **Idle**: ~500MB
- **All Models Loaded**: 4-6GB
- **Per Request**: 50-100MB peak

### Accuracy
- **Fake News BERT**: ~94%
- **Sentiment RoBERTa**: ~92%
- **NLI RoBERTa**: ~88%

### Scalability
- **Handles**: 30+ news items per feed
- **Supported**: ~5-10 concurrent requests
- **For production**: Consider distributed approach

---

Created: November 2024  
Architecture: Microservices with ML Pipeline
Status: Production Ready
