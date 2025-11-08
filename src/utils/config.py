"""Configuration management for the application"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    SERPAPI_KEY: Optional[str] = os.getenv("SERPAPI_KEY")
    CROSSREF_MAILTO: Optional[str] = os.getenv("CROSSREF_MAILTO", "litsearch@example.com")

    # Rate limiting (requests per second)
    PUBMED_RATE_LIMIT: float = float(os.getenv("PUBMED_RATE_LIMIT", "3"))
    SCHOLAR_RATE_LIMIT: float = float(os.getenv("SCHOLAR_RATE_LIMIT", "0.5"))
    ARXIV_RATE_LIMIT: float = float(os.getenv("ARXIV_RATE_LIMIT", "1"))
    CROSSREF_RATE_LIMIT: float = float(os.getenv("CROSSREF_RATE_LIMIT", "2"))

    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    CACHE_DIR: Path = Path(os.getenv("CACHE_DIR", BASE_DIR / "cache"))
    PAPERS_DIR: Path = Path(os.getenv("PAPERS_DIR", BASE_DIR / "papers"))
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "output"))

    # Cache settings
    CACHE_EXPIRY_DAYS: int = int(os.getenv("CACHE_EXPIRY_DAYS", "30"))

    # Debug
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Search settings
    DEFAULT_MAX_RESULTS: int = 50
    MAX_CONCURRENT_REQUESTS: int = 5
    REQUEST_TIMEOUT: int = 30

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.PAPERS_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def has_ai_capabilities(cls) -> bool:
        """Check if AI synthesis is available"""
        return bool(cls.ANTHROPIC_API_KEY or cls.OPENAI_API_KEY)

# Ensure directories exist on import
Config.ensure_directories()