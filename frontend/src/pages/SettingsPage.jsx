import { useState, useEffect } from 'react';
import { FaCheckCircle, FaTimesCircle, FaUpload, FaSpinner } from 'react-icons/fa';
import { authAPI } from '../services/api';
import './SettingsPage.css';

function SettingsPage() {
  const [authStatus, setAuthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);

  useEffect(() => {
    loadAuthStatus();
  }, []);

  const loadAuthStatus = async () => {
    try {
      const response = await authAPI.getStatus();
      setAuthStatus(response.data);
    } catch (error) {
      console.error('Failed to load auth status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    setUploadMessage(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await authAPI.importCookies(formData);

      if (response.data.success) {
        setUploadMessage({ type: 'success', text: '✓ Cookies imported successfully! UCSB access enabled.' });
        await loadAuthStatus();
      } else {
        setUploadMessage({ type: 'error', text: '✗ ' + (response.data.message || 'Failed to import cookies') });
      }
    } catch (error) {
      setUploadMessage({
        type: 'error',
        text: '✗ Failed to import cookies: ' + (error.response?.data?.detail || error.message)
      });
    } finally {
      setUploading(false);
      event.target.value = ''; // Reset file input
    }
  };

  const handleClearAuth = async () => {
    if (!confirm('Are you sure you want to clear UCSB authentication?')) return;

    try {
      await authAPI.clear();
      setUploadMessage({ type: 'success', text: '✓ Authentication cleared successfully' });
      loadAuthStatus();
    } catch (error) {
      setUploadMessage({
        type: 'error',
        text: '✗ Failed to clear authentication: ' + (error.response?.data?.detail || error.message)
      });
    }
  };

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1>⚙️ Settings</h1>
        <p>Manage your application settings</p>
      </div>

      <div className="settings-section">
        <h2>UCSB Library Authentication</h2>

        {loading ? (
          <p>Loading...</p>
        ) : authStatus ? (
          <div className="auth-status">
            <div className={`status-indicator ${authStatus.authenticated ? 'authenticated' : 'not-authenticated'}`}>
              {authStatus.authenticated ? (
                <>
                  <FaCheckCircle size={24} color="#10b981" />
                  <span>Authenticated</span>
                </>
              ) : (
                <>
                  <FaTimesCircle size={24} color="#ef4444" />
                  <span>Not Authenticated</span>
                </>
              )}
            </div>

            <p className="status-message">{authStatus.message}</p>

            <div className="auth-details">
              <p><strong>Session file exists:</strong> {authStatus.session_file_exists ? 'Yes' : 'No'}</p>
              <p><strong>Cookies count:</strong> {authStatus.cookies_count}</p>
            </div>

            {authStatus.authenticated && (
              <button onClick={handleClearAuth} className="btn-danger">
                Clear Authentication
              </button>
            )}
          </div>
        ) : (
          <p>Failed to load authentication status</p>
        )}

        {uploadMessage && (
          <div className={`upload-message ${uploadMessage.type}`}>
            {uploadMessage.text}
          </div>
        )}

        {!authStatus?.authenticated && (
          <div className="cookie-upload-section">
            <h3>🚀 Import UCSB Cookies</h3>
            <p className="upload-description">
              Upload your UCSB library cookies to enable access to paywalled papers!
              This increases download success from ~10% to ~70-80%.
            </p>

            <div className="upload-area">
              <input
                type="file"
                id="cookie-file"
                accept=".txt"
                onChange={handleFileUpload}
                disabled={uploading}
                style={{ display: 'none' }}
              />
              <label htmlFor="cookie-file" className={`upload-button ${uploading ? 'uploading' : ''}`}>
                {uploading ? (
                  <>
                    <FaSpinner className="spinner" />
                    <span>Importing cookies...</span>
                  </>
                ) : (
                  <>
                    <FaUpload />
                    <span>Choose cookies.txt file</span>
                  </>
                )}
              </label>
            </div>

            <div className="auth-instructions">
              <h3>📋 How to enable UCSB access:</h3>
              <ol>
                <li>
                  <strong>Install cookie extension:</strong>
                  <ul>
                    <li>Chrome/Edge: <a href="https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc" target="_blank" rel="noopener noreferrer">"Get cookies.txt LOCALLY"</a></li>
                    <li>Firefox: <a href="https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/" target="_blank" rel="noopener noreferrer">"cookies.txt"</a></li>
                  </ul>
                </li>
                <li>Log in to <a href="https://library.ucsb.edu" target="_blank" rel="noopener noreferrer">library.ucsb.edu</a> with your UCSB NetID</li>
                <li>Complete DUO authentication</li>
                <li>Click the extension icon and export cookies as <code>cookies.txt</code></li>
                <li>Upload the file using the button above</li>
              </ol>
              <div className="note success-note">
                <strong>✨ Benefits:</strong> Access to Nature, Science, Elsevier, Wiley, Springer, and thousands more journals through UCSB subscriptions!
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="settings-section">
        <h2>Application Info</h2>
        <div className="app-info">
          <p><strong>Version:</strong> 1.0.0</p>
          <p><strong>API:</strong> http://localhost:8000/api</p>
          <p><strong>Docs:</strong> <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">Interactive API Docs</a></p>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
