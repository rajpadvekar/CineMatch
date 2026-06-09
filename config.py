import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Project Root Directory
BASE_DIR = Path(__file__).resolve().parent

# Data/Model Paths
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
MOVIES_PKL = MODELS_DIR / "movies.pkl"
SIMILARITY_PKL = MODELS_DIR / "similarity.pkl"
METADATA_PKL = MODELS_DIR / "movie_metadata.pkl"
TMDB_CACHE_FILE = DATA_DIR / "tmdb_cache.json"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"

# API Keys
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

# TMDB Base URL for Poster Images
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def get_active_llm():
    """Determines the active LLM provider based on availability of keys."""
    if LLM_PROVIDER == "groq" and GROQ_API_KEY:
        return "groq"
    elif LLM_PROVIDER == "gemini" and GEMINI_API_KEY:
        return "gemini"
    elif LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        return "openai"
    
    # Fallbacks
    if GROQ_API_KEY:
        return "groq"
    if GEMINI_API_KEY:
        return "gemini"
    if OPENAI_API_KEY:
        return "openai"
    
    return None
