#!/usr/bin/env python3
"""
Quick Setup Guide for Clarifact-AI ML Models Integration

Run this script to verify and setup the environment.
"""

import subprocess
import sys
import os

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def run_command(cmd, description):
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print_header("Clarifact-AI ML Models Integration Setup")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    print_header("Step 1: Installing Dependencies")
    run_command("pip install --upgrade pip", "Upgrading pip")
    run_command("pip install -r requirements.txt", "Installing requirements.txt")
    
    # Download spaCy model
    print_header("Step 2: Downloading NER Model")
    run_command("python -m spacy download en_core_web_sm", "Downloading spaCy model")
    
    # Environment setup
    print_header("Step 3: Environment Configuration")
    
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if not newsapi_key:
        print("\n⚠️  NewsAPI key not found in environment")
        print("   Optional: Get free key from https://newsapi.org")
        print("   Then run: export NEWSAPI_KEY=your_key_here")
    else:
        print("✅ NewsAPI key found")
    
    # Verify imports
    print_header("Step 4: Verifying Package Imports")
    
    packages = [
        ("transformers", "Transformers"),
        ("torch", "PyTorch"),
        ("spacy", "spaCy"),
        ("sentence_transformers", "Sentence Transformers"),
        ("fastapi", "FastAPI"),
        ("feedparser", "FeedParser"),
    ]
    
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Install manually if needed")
    
    # Final instructions
    print_header("Setup Complete!")
    print("""
Next Steps:

1. Start Backend Server:
   cd c:\\Users\\ABHINAV\\Desktop\\Prog\\Projects\\Clarifact-AI
   python backend_server.py
   
   Server will run on http://localhost:8000

2. Start Frontend (in another terminal):
   cd clarifact
   npm install  # if needed
   npm run dev
   
   Frontend will run on http://localhost:3000

3. Test API:
   curl http://localhost:8000/
   curl http://localhost:8000/models

Features Now Available:
✨ Real BERT Fake News Detection (jy46604790/Fake-News-Bert-Detect)
✨ Sentiment Analysis (cardiffnlp/twitter-roberta-base-sentiment)
✨ NLI Contradiction Detection (roberta-large-mnli)
✨ Real News Sources (BBC, Reuters, Guardian, etc.)
✨ Questionable Sources (Breitbart, InfoWars for comparison)
✨ Entertainment Sources (TMZ, Reddit)
✨ NewsAPI Integration (optional)

Note:
- First run will download ~4GB of models (takes 30-60 seconds)
- Requires 4-6GB RAM when all models loaded
- GPU recommended but not required

For detailed documentation, see: ML_MODELS_INTEGRATION.md
    """)

if __name__ == "__main__":
    main()
