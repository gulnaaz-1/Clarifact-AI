import logging
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import spacy
from typing import Optional

logger = logging.getLogger("ViralWarnSystem")

# === Model Configuration ===
FAKE_NEWS_MODEL = "jy46604790/Fake-News-Bert-Detect"
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
NLI_MODEL = "roberta-large-mnli"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SPACY_MODEL = "en_core_web_sm"

# === Lazy-loaded globals ===
_fake_news_clf: Optional[pipeline] = None
_sentiment_clf: Optional[pipeline] = None
_nli_clf: Optional[pipeline] = None
_embed_model: Optional[SentenceTransformer] = None
_spacy_model: Optional[spacy.Language] = None

# === Model Loaders (Lazy Loading) ===

def get_fake_news_model():
    """Load or retrieve Fake News Classification model."""
    global _fake_news_clf
    if _fake_news_clf is None:
        try:
            logger.info(f"Loading Fake News Model: {FAKE_NEWS_MODEL}")
            _fake_news_clf = pipeline(
                "text-classification",
                model=FAKE_NEWS_MODEL,
                tokenizer=FAKE_NEWS_MODEL,
                device=0  # GPU if available, CPU otherwise
            )
            logger.info("Fake News model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load fake news model: {e}")
            raise
    return _fake_news_clf

def get_sentiment_model():
    """Load or retrieve Sentiment Analysis model."""
    global _sentiment_clf
    if _sentiment_clf is None:
        try:
            logger.info(f"Loading Sentiment Model: {SENTIMENT_MODEL}")
            _sentiment_clf = pipeline(
                "text-classification",
                model=SENTIMENT_MODEL,
                device=0
            )
            logger.info("Sentiment model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            raise
    return _sentiment_clf

def get_nli_model():
    """Load or retrieve Natural Language Inference model for contradiction detection."""
    global _nli_clf
    if _nli_clf is None:
        try:
            logger.info(f"Loading NLI Model: {NLI_MODEL}")
            _nli_clf = pipeline(
                "zero-shot-classification",
                model=NLI_MODEL,
                device=0
            )
            logger.info("NLI model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load NLI model: {e}")
            raise
    return _nli_clf

def get_embed_model():
    """Load or retrieve Sentence Embedding model for similarity analysis."""
    global _embed_model
    if _embed_model is None:
        try:
            logger.info(f"Loading Embedding Model: {EMBEDDING_MODEL}")
            _embed_model = SentenceTransformer(EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    return _embed_model

def get_spacy_model():
    """Load or retrieve Spacy NLP model for NER and linguistic analysis."""
    global _spacy_model
    if _spacy_model is None:
        try:
            logger.info(f"Loading Spacy Model: {SPACY_MODEL}")
            _spacy_model = spacy.load(SPACY_MODEL)
            logger.info("Spacy model loaded successfully")
        except OSError:
            logger.warning(f"Spacy model {SPACY_MODEL} not found. Downloading...")
            import os
            os.system(f"python -m spacy download {SPACY_MODEL}")
            _spacy_model = spacy.load(SPACY_MODEL)
        except Exception as e:
            logger.error(f"Failed to load spacy model: {e}")
            raise
    return _spacy_model

# === Unload functions for memory management ===

def unload_all_models():
    """Unload all models from memory."""
    global _fake_news_clf, _sentiment_clf, _nli_clf, _embed_model, _spacy_model
    _fake_news_clf = None
    _sentiment_clf = None
    _nli_clf = None
    _embed_model = None
    _spacy_model = None
    logger.info("All models unloaded from memory")

# === Quick initialization check ===

def check_models_available():
    """Check if all required models are available (without loading them fully)."""
    models_info = {
        "fake_news": FAKE_NEWS_MODEL,
        "sentiment": SENTIMENT_MODEL,
        "nli": NLI_MODEL,
        "embedding": EMBEDDING_MODEL,
        "spacy": SPACY_MODEL
    }
    return models_info
