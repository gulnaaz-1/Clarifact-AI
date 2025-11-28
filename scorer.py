# scorer.py - compute risk scores using real ML models
import time
import requests
import re
from typing import Dict, List
import logging
from config import USE_HEAVY_MODELS, WIKIPEDIA_TIMEOUT
from sentence_transformers import util

# Import from our centralized models module
from models import (
    get_fake_news_model,
    get_sentiment_model,
    get_nli_model,
    get_embed_model,
    get_spacy_model
)

logger = logging.getLogger("ViralWarnSystem")

# Fallback keyword lists for heuristic fallback
SENSATIONAL_KEYWORDS = [
    "shocking", "breaking", "miracle", "unbelievable", "viral", "explosive", 
    "urgent", "alert", "danger", "scandal", "exclusive", "exposé"
]

TRUSTED_DOMAINS = [
    "wikipedia.org", "nytimes.com", "bbc.co", "theguardian.com",
    "reuters.com", "apnews.com", "npr.org", "pbs.org"
]

LOW_TRUST_DOMAINS = [
    "blogspot", "wordpress.com", "medium.com", "tumblr.com"
]

def sensational_score(text: str) -> float:
    """
    Score text for sensationalism using both keyword matching and model inference.
    Returns float 0-1 where 1 is most sensational.
    """
    t = text.lower()
    
    # Keyword-based heuristic
    kw_hits = sum(1 for k in SENSATIONAL_KEYWORDS if k in t)
    keyword_score = min(1.0, kw_hits / 5.0)
    
    if USE_HEAVY_MODELS:
        try:
            # Use sentiment model as proxy for sensationalism
            # Negative sentiment often correlates with sensationalism
            sentiment_clf = get_sentiment_model()
            output = sentiment_clf(text[:256])[0]
            label = output["label"].upper()
            score = output["score"]
            
            # Negative (LABEL_0) is more sensational
            if "LABEL_0" in label or "NEGATIVE" in label:
                model_score = score
            else:
                model_score = 0.1
            
            # Combine both scores
            return max(keyword_score, model_score * 0.8)
        except Exception as e:
            logger.debug(f"Error in sensational_score model inference: {e}")
            return keyword_score
    
    return keyword_score

def source_credibility(url: str) -> float:
    """
    Score source credibility based on domain reputation.
    Returns float 0-1 where 1 is most credible.
    """
    if not url:
        return 0.5
    
    url_lower = url.lower()
    
    # Check trusted domains
    for trusted_domain in TRUSTED_DOMAINS:
        if trusted_domain in url_lower:
            return 0.9
    
    # Check low-trust domains
    for untrusted_domain in LOW_TRUST_DOMAINS:
        if untrusted_domain in url_lower:
            return 0.3
    
    # Default for unknown domains
    return 0.5

def extract_claims(text: str, max_claims: int = 3) -> List[str]:
    """
    Extract key claims from text using NER and sentence segmentation.
    """
    try:
        nlp = get_spacy_model()
        doc = nlp(text[:1000])
        
        claims = []
        
        # Extract noun chunks as claims
        for nc in doc.noun_chunks:
            s = str(nc).strip()
            if 8 < len(s) < 150 and len(s.split()) <= 8:
                claims.append(s)
        
        # If not enough claims, fall back to sentences with entities
        if len(claims) < max_claims:
            for sent in doc.sents:
                if any(ent for ent in sent.ents) and len(sent.text) > 15:
                    claims.append(sent.text.strip())
        
        return claims[:max_claims]
    
    except Exception as e:
        logger.debug(f"Error extracting claims: {e}")
        # Fallback: split by sentences
        sents = re.split(r'(?<=[.!?]) +', text)
        return [s for s in sents if len(s) > 40][:max_claims]

def quick_wikipedia_search(query: str) -> dict:
    """
    Quick Wikipedia search for evidence verification.
    """
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query[:200],
            "format": "json"
        }
        r = requests.get(url, params=params, timeout=WIKIPEDIA_TIMEOUT)
        
        if r.ok:
            data = r.json()
            hits = data.get("query", {}).get("search", [])
            if hits:
                return {
                    "title": hits[0]["title"],
                    "snippet": hits[0].get("snippet", ""),
                    "page": "https://en.wikipedia.org/wiki/" + hits[0]["title"].replace(' ', '_')
                }
    except Exception as e:
        logger.debug(f"Wikipedia search error: {e}")
    
    return {}

def contradiction_score(claims: List[str], evidence_snippets: List[str]) -> float:
    """
    Detect contradictions between claims and evidence using NLI model.
    Returns float 0-1 where 1 means highly contradictory.
    """
    if not claims or not evidence_snippets:
        return 0.0
    
    if USE_HEAVY_MODELS:
        try:
            nli_clf = get_nli_model()
            contradictions = 0
            total = 0
            
            for claim in claims[:3]:
                for evidence in evidence_snippets[:3]:
                    if not evidence or not claim:
                        continue
                    
                    total += 1
                    
                    # Use NLI model to detect contradiction
                    # premise is evidence, hypothesis is claim
                    text = f"{evidence} </s> {claim}"
                    
                    output = nli_clf(text[:512], ["contradiction", "entailment", "neutral"])
                    
                    if output and len(output) > 0:
                        # Find contradiction score
                        for label_obj in output:
                            if "contradiction" in label_obj.get("label", "").lower():
                                if label_obj.get("score", 0) > 0.5:
                                    contradictions += 1
                                break
            
            return (contradictions / total) if total > 0 else 0.0
        
        except Exception as e:
            logger.debug(f"Error in contradiction detection: {e}")
    
    # Fallback: embedding similarity
    try:
        embed_model = get_embed_model()
        claim_embeddings = embed_model.encode(claims, convert_to_tensor=True)
        evidence_embeddings = embed_model.encode(evidence_snippets, convert_to_tensor=True)
        
        similarity = util.pytorch_cos_sim(claim_embeddings, evidence_embeddings).mean().item()
        
        # Lower similarity suggests contradiction
        return max(0.0, min(1.0, 1.0 - similarity))
    
    except Exception as e:
        logger.debug(f"Error in embedding similarity: {e}")
        return 0.0

def fake_news_score(text: str) -> float:
    """
    Score text likelihood of being fake news using BERT model.
    Returns float 0-1 where 1 is definitely fake.
    """
    try:
        clf = get_fake_news_model()
        output = clf(text[:512])[0]
        
        label = output["label"].upper()
        score = output["score"]
        
        # If model says FAKE, return score as-is
        # If model says REAL, return inverse
        if "FAKE" in label:
            return score
        else:
            return 1.0 - score
    
    except Exception as e:
        logger.error(f"Error in fake news detection: {e}")
        return 0.5

def compute_risk(post: Dict) -> Dict:
    """
    Comprehensive risk scoring function combining multiple ML models.
    """
    text = (post.get('title', '') + ". " + post.get('text', ''))[:2000]
    url = post.get('url', '')
    
    try:
        # Compute individual risk components
        fake_score = fake_news_score(text)
        sensational = sensational_score(text)
        source_cred = source_credibility(url)
        
        claims = extract_claims(text)
        evidence = [quick_wikipedia_search(c).get('snippet', "") for c in claims]
        contradiction = contradiction_score(claims, evidence)
        
        # Virality estimation from text (look for metrics)
        virality = 0.0
        virality_match = re.search(r'(\d{2,})\s*(upvote|points|upvotes|score|view|like)', text.lower())
        if virality_match:
            val = int(virality_match.group(1))
            virality = min(1.0, val / 10000.0)
        
        # Weighted combination
        weights = {
            'fake_news': 0.35,
            'sensational': 0.25,
            'contradiction': 0.20,
            'source_credibility': 0.15,
            'virality': 0.05
        }
        
        risk_score = (
            weights['fake_news'] * fake_score +
            weights['sensational'] * sensational +
            weights['contradiction'] * contradiction +
            weights['source_credibility'] * (1 - source_cred) +
            weights['virality'] * virality
        )
        
        risk_score = max(0.0, min(1.0, risk_score))
        
        return {
            'risk_score': risk_score,
            'components': {
                'fake_news': round(fake_score, 3),
                'sensational': round(sensational, 3),
                'contradiction': round(contradiction, 3),
                'source_score': round(source_cred, 3),
                'virality': round(virality, 3)
            },
            'claims': claims,
            'evidence': evidence,
            'reasoning': (
                f"Fake News: {fake_score:.2f}, "
                f"Sensationalism: {sensational:.2f}, "
                f"Contradiction: {contradiction:.2f}, "
                f"Source Credibility: {source_cred:.2f}"
            )
        }
    
    except Exception as e:
        logger.error(f"Error computing risk: {e}")
        # Fallback: return neutral score
        return {
            'risk_score': 0.5,
            'components': {
                'fake_news': 0.5,
                'sensational': 0.3,
                'contradiction': 0.2,
                'source_score': 0.5,
                'virality': 0.0
            },
            'claims': extract_claims(text),
            'evidence': [],
            'reasoning': "Error in analysis - using fallback score"
        }
