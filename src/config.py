"""Configuration settings and constants for the Study Assistant RAG system."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (or .env.example fallback)
load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    env_example = Path(__file__).resolve().parent.parent / ".env.example"
    if env_example.exists():
        load_dotenv(dotenv_path=env_example)

# Embedding and Retrieval parameters
EMBED_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE: int = 800  # characters
CHUNK_OVERLAP: int = 150  # characters
TOP_K: int = 4
SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.20"))

# Optional LLM generation parameters
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY") or None
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Check Streamlit Community Cloud secrets if present
if not GEMINI_API_KEY:
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        if hasattr(st, "secrets") and "GEMINI_MODEL" in st.secrets:
            GEMINI_MODEL = st.secrets["GEMINI_MODEL"]
    except Exception:
        pass

# Project directories
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
SAMPLE_DATA_DIR: Path = DATA_DIR / "sample"
