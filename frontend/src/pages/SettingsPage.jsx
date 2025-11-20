import { useState, useEffect } from 'react';
import { FaCheckCircle, FaTimesCircle, FaUpload, FaSpinner } from 'react-icons/fa';
import { authAPI } from '../services/api';

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
    <div className="space-y-8 max-w-4xl mx-auto animate-fade-in">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 dark:text-slate-50">
          ⚙️ Settings
        </h1>
        <p className="text-base text-slate-600 dark:text-slate-400">
          Manage your application settings
        </p>
      </div>

      {/* UCSB Authentication Section */}
      <div className="card space-y-6">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
          UCSB Library Authentication
        </h2>

        {loading ? (
          <p className="text-slate-600 dark:text-slate-400">Loading...</p>
        ) : authStatus ? (
          <div className="space-y-6">
            {/* Status Indicator */}
            <div className={`
              flex items-center gap-3 p-4 rounded-lg
              ${authStatus.authenticated
                ? 'bg-success-50 dark:bg-success-950/30 border border-success-200 dark:border-success-800'
                : 'bg-error-50 dark:bg-error-950/30 border border-error-200 dark:border-error-800'
              }
            `}>
              {authStatus.authenticated ? (
                <>
                  <FaCheckCircle size={24} className="text-success-600 dark:text-success-400 flex-shrink-0" />
                  <span className="font-semibold text-success-900 dark:text-success-100">Authenticated</span>
                </>
              ) : (
                <>
                  <FaTimesCircle size={24} className="text-error-600 dark:text-error-400 flex-shrink-0" />
                  <span className="font-semibold text-error-900 dark:text-error-100">Not Authenticated</span>
                </>
              )}
            </div>

            <p className="text-slate-700 dark:text-slate-300">{authStatus.message}</p>

            {/* Auth Details */}
            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="font-medium text-slate-700 dark:text-slate-300">Session file exists:</span>
                <span className="text-slate-900 dark:text-slate-50">{authStatus.session_file_exists ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium text-slate-700 dark:text-slate-300">Cookies count:</span>
                <span className="text-slate-900 dark:text-slate-50">{authStatus.cookies_count}</span>
              </div>
            </div>

            {authStatus.authenticated && (
              <button
                onClick={handleClearAuth}
                className="btn bg-error-600 hover:bg-error-700 text-white"
              >
                Clear Authentication
              </button>
            )}
          </div>
        ) : (
          <p className="text-error-600 dark:text-error-400">Failed to load authentication status</p>
        )}

        {/* Upload Message */}
        {uploadMessage && (
          <div className={`
            p-4 rounded-lg text-sm
            ${uploadMessage.type === 'success'
              ? 'bg-success-50 dark:bg-success-950/30 text-success-900 dark:text-success-100 border border-success-200 dark:border-success-800'
              : 'bg-error-50 dark:bg-error-950/30 text-error-900 dark:text-error-100 border border-error-200 dark:border-error-800'
            }
          `}>
            {uploadMessage.text}
          </div>
        )}

        {/* Cookie Upload Section */}
        {!authStatus?.authenticated && (
          <div className="space-y-6 pt-4 border-t border-slate-200 dark:border-slate-700">
            <div className="space-y-2">
              <h3 className="text-xl font-bold text-slate-900 dark:text-slate-50">
                🚀 Import UCSB Cookies
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Upload your UCSB library cookies to enable access to paywalled papers!
                This increases download success from ~10% to ~70-80%.
              </p>
            </div>

            {/* Upload Button */}
            <div className="flex justify-center">
              <input
                type="file"
                id="cookie-file"
                accept=".txt"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
              />
              <label
                htmlFor="cookie-file"
                className={`
                  btn-primary cursor-pointer inline-flex items-center gap-2
                  ${uploading ? 'opacity-75 cursor-wait' : ''}
                `}
              >
                {uploading ? (
                  <>
                    <FaSpinner className="animate-spin" />
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

            {/* Instructions */}
            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-6 space-y-4">
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-50">
                📋 How to enable UCSB access:
              </h3>
              <ol className="space-y-3 text-sm text-slate-700 dark:text-slate-300 list-decimal list-inside">
                <li>
                  <strong className="text-slate-900 dark:text-slate-50">Install cookie extension:</strong>
                  <ul className="ml-6 mt-2 space-y-1 list-disc list-inside">
                    <li>
                      Chrome/Edge:{' '}
                      <a
                        href="https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 dark:text-primary-400 hover:underline"
                      >
                        "Get cookies.txt LOCALLY"
                      </a>
                    </li>
                    <li>
                      Firefox:{' '}
                      <a
                        href="https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 dark:text-primary-400 hover:underline"
                      >
                        "cookies.txt"
                      </a>
                    </li>
                  </ul>
                </li>
                <li>
                  Log in to{' '}
                  <a
                    href="https://library.ucsb.edu"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 dark:text-primary-400 hover:underline"
                  >
                    library.ucsb.edu
                  </a>{' '}
                  with your UCSB NetID
                </li>
                <li>Complete DUO authentication</li>
                <li>
                  Click the extension icon and export cookies as{' '}
                  <code className="px-1.5 py-0.5 bg-slate-200 dark:bg-slate-700 rounded text-xs">cookies.txt</code>
                </li>
                <li>Upload the file using the button above</li>
              </ol>
              <div className="bg-success-50 dark:bg-success-950/30 border-l-4 border-success-500 p-4 rounded-r-lg">
                <p className="text-sm text-success-900 dark:text-success-100">
                  <strong>✨ Benefits:</strong> Access to Nature, Science, Elsevier, Wiley, Springer, and thousands more journals through UCSB subscriptions!
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Application Info Section */}
      <div className="card space-y-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
          Application Info
        </h2>
        <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="font-medium text-slate-700 dark:text-slate-300">Version:</span>
            <span className="text-slate-900 dark:text-slate-50">1.0.0</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium text-slate-700 dark:text-slate-300">API:</span>
            <span className="text-slate-900 dark:text-slate-50">http://localhost:8000/api</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium text-slate-700 dark:text-slate-300">Docs:</span>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 dark:text-primary-400 hover:underline"
            >
              Interactive API Docs
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
