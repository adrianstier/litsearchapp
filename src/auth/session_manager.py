"""Simple session management for HTTP requests"""

import pickle
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import requests
from src.utils.config import Config


class SessionManager:
    """Manage HTTP sessions with caching"""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize session manager"""
        self.cache_dir = cache_dir or Config.CACHE_DIR
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LiteratureSearchBot/1.0 (Academic Research Tool)'
        })

    def save_cookies(self, filename: str = "session_cookies.pkl"):
        """Save session cookies to disk"""
        filepath = self.cache_dir / filename
        with open(filepath, 'wb') as f:
            pickle.dump(self.session.cookies, f)

    def load_cookies(self, filename: str = "session_cookies.pkl") -> bool:
        """Load session cookies from disk"""
        filepath = self.cache_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'rb') as f:
                    cookies = pickle.load(f)
                    self.session.cookies.update(cookies)
                return True
            except Exception as e:
                print(f"Failed to load cookies: {e}")
        return False

    def get_session(self) -> requests.Session:
        """Get the current session"""
        return self.session

    def set_header(self, key: str, value: str):
        """Set a header for all requests"""
        self.session.headers[key] = value

    def clear_session(self):
        """Clear the current session"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LiteratureSearchBot/1.0 (Academic Research Tool)'
        })