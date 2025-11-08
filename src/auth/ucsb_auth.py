"""UCSB Library authentication via cookie import"""

import os
import pickle
import http.cookiejar
from pathlib import Path
from typing import Optional
from datetime import datetime
import requests
from src.utils.config import Config


class UCSBAuth:
    """Manage UCSB library authentication via imported cookies"""

    def __init__(self):
        """Initialize UCSB authentication manager"""
        # Create config directory
        self.config_dir = Path.home() / ".config" / "litsearch"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Set restrictive permissions on config directory
        try:
            os.chmod(self.config_dir, 0o700)
        except:
            pass

        self.cookies_file = self.config_dir / "ucsb_cookies.txt"
        self.session_file = self.config_dir / "ucsb_session.pkl"

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        self.proxy_base = "https://proxy.library.ucsb.edu/login?url="
        self.is_authenticated = False

    def import_cookies_netscape(self, cookies_file: Path) -> bool:
        """
        Import cookies from Netscape format (cookies.txt)

        Args:
            cookies_file: Path to cookies.txt file

        Returns:
            True if import successful
        """
        if not cookies_file.exists():
            raise FileNotFoundError(f"Cookie file not found: {cookies_file}")

        try:
            # Create a cookie jar and load from Netscape format
            cookie_jar = http.cookiejar.MozillaCookieJar()
            cookie_jar.load(str(cookies_file), ignore_discard=True, ignore_expires=True)

            # Transfer cookies to requests session
            for cookie in cookie_jar:
                self.session.cookies.set_cookie(cookie)

            # Save session
            self._save_session()

            # Test if session works
            if self.test_session():
                self.is_authenticated = True
                print("✓ Cookies imported successfully")
                print(f"✓ Session authenticated with UCSB library")
                return True
            else:
                print("⚠ Cookies imported but session test failed")
                print("  Try logging into library.ucsb.edu and exporting fresh cookies")
                return False

        except Exception as e:
            print(f"✗ Failed to import cookies: {e}")
            return False

    def import_cookies_json(self, cookies_file: Path) -> bool:
        """
        Import cookies from JSON format (alternative format)

        Args:
            cookies_file: Path to cookies JSON file

        Returns:
            True if import successful
        """
        import json

        if not cookies_file.exists():
            raise FileNotFoundError(f"Cookie file not found: {cookies_file}")

        try:
            with open(cookies_file, 'r') as f:
                cookies = json.load(f)

            # Add cookies to session
            for cookie in cookies:
                self.session.cookies.set(
                    cookie.get('name'),
                    cookie.get('value'),
                    domain=cookie.get('domain'),
                    path=cookie.get('path', '/')
                )

            # Save and test
            self._save_session()

            if self.test_session():
                self.is_authenticated = True
                print("✓ Cookies imported successfully")
                return True
            else:
                print("⚠ Cookies imported but session test failed")
                return False

        except Exception as e:
            print(f"✗ Failed to import cookies: {e}")
            return False

    def load_session(self) -> bool:
        """
        Load previously saved session

        Returns:
            True if session loaded and valid
        """
        if not self.session_file.exists():
            return False

        try:
            with open(self.session_file, 'rb') as f:
                cookies = pickle.load(f)
                self.session.cookies.update(cookies)

            # Test if session is still valid
            if self.test_session():
                self.is_authenticated = True
                return True
            else:
                # Session expired
                self.clear_session()
                return False

        except Exception as e:
            print(f"⚠ Failed to load session: {e}")
            return False

    def _save_session(self):
        """Save session cookies to disk"""
        try:
            with open(self.session_file, 'wb') as f:
                pickle.dump(self.session.cookies, f)

            # Set restrictive permissions
            os.chmod(self.session_file, 0o600)

        except Exception as e:
            print(f"⚠ Failed to save session: {e}")

    def test_session(self) -> bool:
        """
        Test if current session is authenticated with UCSB

        Returns:
            True if authenticated
        """
        try:
            # Try to access a known proxied URL
            test_url = "https://proxy.library.ucsb.edu/login"
            response = self.session.get(test_url, timeout=10, allow_redirects=True)

            # Check if we're logged in (not redirected to login page)
            # If authenticated, we should see "logout" or similar
            content = response.text.lower()

            # Simple heuristic: if we see login form, we're not authenticated
            if 'netid' in content and 'password' in content:
                return False

            # If we see logout or success indicators, we're authenticated
            if 'logout' in content or 'authenticated' in content:
                return True

            # Check cookies for UCSB-specific authentication cookies
            has_auth_cookies = any(
                'ezproxy' in cookie.name.lower() or
                'session' in cookie.name.lower()
                for cookie in self.session.cookies
            )

            return has_auth_cookies

        except Exception as e:
            print(f"⚠ Session test failed: {e}")
            return False

    def get_session(self) -> requests.Session:
        """
        Get authenticated session

        Returns:
            Requests session with UCSB authentication
        """
        return self.session

    def get_proxied_url(self, url: str) -> str:
        """
        Convert URL to UCSB proxy format

        Args:
            url: Original URL

        Returns:
            Proxied URL
        """
        return f"{self.proxy_base}{url}"

    def clear_session(self):
        """Clear saved session and cookies"""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            if self.cookies_file.exists():
                self.cookies_file.unlink()

            self.session.cookies.clear()
            self.is_authenticated = False

            print("✓ Session cleared")

        except Exception as e:
            print(f"⚠ Failed to clear session: {e}")

    def get_status(self) -> dict:
        """
        Get authentication status

        Returns:
            Dictionary with status information
        """
        status = {
            'authenticated': self.is_authenticated,
            'session_file_exists': self.session_file.exists(),
            'cookies_count': len(self.session.cookies),
            'config_dir': str(self.config_dir)
        }

        if self.is_authenticated:
            status['message'] = "✓ Authenticated with UCSB library"
        else:
            status['message'] = "✗ Not authenticated - import cookies to enable institutional access"

        return status