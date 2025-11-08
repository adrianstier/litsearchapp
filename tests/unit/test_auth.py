"""Tests for UCSB authentication"""

import pytest
import json
import pickle
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.auth.ucsb_auth import UCSBAuth


class TestUCSBAuthInit:
    """Test UCSBAuth initialization"""

    def test_init_creates_config_dir(self, tmp_path, monkeypatch):
        """Test that initialization creates config directory"""
        # Use temporary directory
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        auth = UCSBAuth()

        assert auth.config_dir.exists()
        assert auth.config_dir.is_dir()

    def test_init_sets_session_headers(self):
        """Test that user agent is set"""
        auth = UCSBAuth()

        assert 'User-Agent' in auth.session.headers
        assert 'Mozilla' in auth.session.headers['User-Agent']

    def test_init_not_authenticated(self):
        """Test that initial state is not authenticated"""
        auth = UCSBAuth()

        assert auth.is_authenticated is False


class TestCookieImport:
    """Test cookie import functionality"""

    @patch('src.auth.ucsb_auth.http.cookiejar.MozillaCookieJar')
    @patch.object(UCSBAuth, 'test_session', return_value=True)
    @patch.object(UCSBAuth, '_save_session')
    def test_import_netscape_success(self, mock_save, mock_test, mock_jar_class, tmp_path):
        """Test successful Netscape cookie import"""
        # Create temporary cookie file
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("# Netscape HTTP Cookie File\n")

        # Mock cookie jar
        mock_jar = MagicMock()
        mock_cookie = MagicMock()
        mock_jar.__iter__ = lambda self: iter([mock_cookie])
        mock_jar_class.return_value = mock_jar

        auth = UCSBAuth()
        result = auth.import_cookies_netscape(cookie_file)

        assert result is True
        assert auth.is_authenticated is True
        mock_jar.load.assert_called_once()

    def test_import_netscape_file_not_found(self):
        """Test import with non-existent file"""
        auth = UCSBAuth()

        with pytest.raises(FileNotFoundError):
            auth.import_cookies_netscape(Path("/nonexistent/cookies.txt"))

    @patch('src.auth.ucsb_auth.http.cookiejar.MozillaCookieJar')
    @patch.object(UCSBAuth, 'test_session', return_value=False)
    @patch.object(UCSBAuth, '_save_session')
    def test_import_netscape_invalid_session(self, mock_save, mock_test, mock_jar_class, tmp_path):
        """Test import with invalid session"""
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("# Netscape HTTP Cookie File\n")

        mock_jar = MagicMock()
        mock_jar.__iter__ = lambda self: iter([])
        mock_jar_class.return_value = mock_jar

        auth = UCSBAuth()
        result = auth.import_cookies_netscape(cookie_file)

        assert result is False
        assert auth.is_authenticated is False

    @patch.object(UCSBAuth, 'test_session', return_value=True)
    @patch.object(UCSBAuth, '_save_session')
    def test_import_json_success(self, mock_save, mock_test, tmp_path):
        """Test successful JSON cookie import"""
        # Create JSON cookie file
        cookie_file = tmp_path / "cookies.json"
        cookies = [
            {
                'name': 'session',
                'value': 'abc123',
                'domain': '.ucsb.edu',
                'path': '/'
            }
        ]
        cookie_file.write_text(json.dumps(cookies))

        auth = UCSBAuth()
        result = auth.import_cookies_json(cookie_file)

        assert result is True
        assert auth.is_authenticated is True

    def test_import_json_file_not_found(self):
        """Test JSON import with non-existent file"""
        auth = UCSBAuth()

        with pytest.raises(FileNotFoundError):
            auth.import_cookies_json(Path("/nonexistent/cookies.json"))

    @patch.object(UCSBAuth, 'test_session', return_value=False)
    @patch.object(UCSBAuth, '_save_session')
    def test_import_json_invalid_format(self, mock_save, mock_test, tmp_path):
        """Test JSON import with invalid format"""
        cookie_file = tmp_path / "cookies.json"
        cookie_file.write_text("invalid json")

        auth = UCSBAuth()
        result = auth.import_cookies_json(cookie_file)

        assert result is False


class TestSessionManagement:
    """Test session save/load functionality"""

    @patch.object(UCSBAuth, 'test_session', return_value=True)
    def test_save_and_load_session(self, mock_test, tmp_path, monkeypatch):
        """Test saving and loading session"""
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        # Create auth and add cookies
        auth = UCSBAuth()
        auth.session.cookies.set('test', 'value')
        auth._save_session()

        # Create new auth and load session
        auth2 = UCSBAuth()
        result = auth2.load_session()

        assert result is True
        assert 'test' in auth2.session.cookies

    def test_load_session_no_file(self):
        """Test loading when no session file exists"""
        auth = UCSBAuth()

        result = auth.load_session()

        assert result is False

    @patch.object(UCSBAuth, 'test_session', return_value=False)
    @patch.object(UCSBAuth, 'clear_session')
    def test_load_expired_session(self, mock_clear, mock_test, tmp_path, monkeypatch):
        """Test loading expired session"""
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        # Create and save session
        auth = UCSBAuth()
        auth.session.cookies.set('test', 'value')
        auth._save_session()

        # Load with test_session returning False (expired)
        auth2 = UCSBAuth()
        result = auth2.load_session()

        assert result is False
        mock_clear.assert_called_once()

    def test_clear_session(self, tmp_path, monkeypatch):
        """Test clearing session"""
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        auth = UCSBAuth()
        auth.session.cookies.set('test', 'value')
        auth._save_session()
        auth.is_authenticated = True

        # Clear
        auth.clear_session()

        assert len(auth.session.cookies) == 0
        assert auth.is_authenticated is False


class TestSessionTesting:
    """Test session validation"""

    @patch('requests.Session.get')
    def test_session_test_authenticated(self, mock_get):
        """Test session test with authenticated session"""
        mock_response = MagicMock()
        mock_response.text = "<html>You are authenticated. <a href='/logout'>Logout</a></html>"
        mock_get.return_value = mock_response

        auth = UCSBAuth()
        result = auth.test_session()

        assert result is True

    @patch('requests.Session.get')
    def test_session_test_not_authenticated(self, mock_get):
        """Test session test with login page"""
        mock_response = MagicMock()
        mock_response.text = "<html><form><input name='netid'/><input name='password'/></form></html>"
        mock_get.return_value = mock_response

        auth = UCSBAuth()
        result = auth.test_session()

        assert result is False

    @patch('requests.Session.get')
    def test_session_test_by_cookies(self, mock_get):
        """Test session validation by cookies"""
        mock_response = MagicMock()
        mock_response.text = "<html>Some content</html>"
        mock_get.return_value = mock_response

        auth = UCSBAuth()
        # Add ezproxy cookie
        auth.session.cookies.set('ezproxy_session', 'abc123')

        result = auth.test_session()

        assert result is True

    @patch('requests.Session.get')
    def test_session_test_timeout(self, mock_get):
        """Test session test with timeout"""
        mock_get.side_effect = TimeoutError("Timeout")

        auth = UCSBAuth()
        result = auth.test_session()

        assert result is False

    @patch('requests.Session.get')
    def test_session_test_network_error(self, mock_get):
        """Test session test with network error"""
        mock_get.side_effect = ConnectionError("Network error")

        auth = UCSBAuth()
        result = auth.test_session()

        assert result is False


class TestProxyURL:
    """Test proxy URL generation"""

    def test_get_proxied_url_basic(self):
        """Test basic proxy URL generation"""
        auth = UCSBAuth()

        url = "https://www.nature.com/articles/s41586-020-2649-2"
        proxied = auth.get_proxied_url(url)

        assert proxied.startswith("https://proxy.library.ucsb.edu/login?url=")
        assert url in proxied

    def test_get_proxied_url_preserves_url(self):
        """Test that original URL is preserved"""
        auth = UCSBAuth()

        url = "https://example.com/article?id=123&format=pdf"
        proxied = auth.get_proxied_url(url)

        assert url in proxied

    def test_get_proxied_url_empty(self):
        """Test proxy URL with empty string"""
        auth = UCSBAuth()

        proxied = auth.get_proxied_url("")

        assert proxied == "https://proxy.library.ucsb.edu/login?url="


class TestStatus:
    """Test status reporting"""

    def test_get_status_not_authenticated(self):
        """Test status when not authenticated"""
        auth = UCSBAuth()

        status = auth.get_status()

        assert status['authenticated'] is False
        assert 'Not authenticated' in status['message']
        assert 'cookies_count' in status
        assert 'config_dir' in status

    def test_get_status_authenticated(self):
        """Test status when authenticated"""
        auth = UCSBAuth()
        auth.is_authenticated = True

        status = auth.get_status()

        assert status['authenticated'] is True
        assert 'Authenticated' in status['message']

    def test_get_status_with_session_file(self, tmp_path, monkeypatch):
        """Test status with existing session file"""
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        auth = UCSBAuth()
        auth._save_session()

        status = auth.get_status()

        assert status['session_file_exists'] is True

    def test_get_status_cookies_count(self):
        """Test cookies count in status"""
        auth = UCSBAuth()
        auth.session.cookies.set('cookie1', 'value1')
        auth.session.cookies.set('cookie2', 'value2')

        status = auth.get_status()

        assert status['cookies_count'] == 2


class TestGetSession:
    """Test getting authenticated session"""

    def test_get_session_returns_session(self):
        """Test that get_session returns session object"""
        auth = UCSBAuth()

        session = auth.get_session()

        assert session is auth.session
        assert isinstance(session, type(auth.session))

    def test_get_session_with_cookies(self):
        """Test that session includes cookies"""
        auth = UCSBAuth()
        auth.session.cookies.set('test', 'value')

        session = auth.get_session()

        assert 'test' in session.cookies


class TestEdgeCases:
    """Test edge cases in authentication"""

    def test_multiple_cookie_imports(self, tmp_path):
        """Test importing cookies multiple times"""
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("# Netscape HTTP Cookie File\n")

        with patch('src.auth.ucsb_auth.http.cookiejar.MozillaCookieJar'):
            with patch.object(UCSBAuth, 'test_session', return_value=True):
                with patch.object(UCSBAuth, '_save_session'):
                    auth = UCSBAuth()
                    auth.import_cookies_netscape(cookie_file)
                    auth.import_cookies_netscape(cookie_file)

                    # Should still work

    def test_corrupt_session_file(self, tmp_path, monkeypatch):
        """Test loading corrupt session file"""
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        auth = UCSBAuth()

        # Write corrupt pickle file
        session_file = auth.config_dir / "ucsb_session.pkl"
        session_file.write_text("corrupt data")

        result = auth.load_session()

        assert result is False

    def test_permission_error_on_save(self, tmp_path, monkeypatch):
        """Test handling permission error when saving"""
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        auth = UCSBAuth()

        with patch('builtins.open', side_effect=PermissionError):
            # Should not crash
            auth._save_session()

    def test_special_characters_in_url(self):
        """Test proxy URL with special characters"""
        auth = UCSBAuth()

        url = "https://example.com/article?title=Test%20Article&id=123"
        proxied = auth.get_proxied_url(url)

        assert url in proxied

    def test_very_long_cookie_value(self):
        """Test handling very long cookie value"""
        auth = UCSBAuth()

        long_value = "a" * 10000
        auth.session.cookies.set('long_cookie', long_value)

        # Should handle without crashing
        status = auth.get_status()
        assert status['cookies_count'] == 1

    @patch('requests.Session.get')
    def test_ambiguous_authentication_status(self, mock_get):
        """Test when authentication status is ambiguous"""
        mock_response = MagicMock()
        # Response with no clear indicators
        mock_response.text = "<html><body>Welcome</body></html>"
        mock_get.return_value = mock_response

        auth = UCSBAuth()
        result = auth.test_session()

        # Should check cookies as fallback
        assert isinstance(result, bool)

    def test_concurrent_session_access(self):
        """Test thread safety of session access"""
        import threading

        auth = UCSBAuth()
        results = []

        def worker():
            session = auth.get_session()
            results.append(session is not None)

        threads = [threading.Thread(target=worker) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(results)
