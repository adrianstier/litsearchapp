import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
  SearchIcon, BookIcon, FolderIcon, ChartIcon, SettingsIcon,
  CheckCircleIcon, XCircleIcon, SunIcon, MoonIcon, MenuIcon, CloseIcon
} from './components/Icons';
import SearchPage from './pages/SearchPage';
import LibraryPage from './pages/LibraryPage';
import CollectionsPage from './pages/CollectionsPage';
import VisualizationsPage from './pages/VisualizationsPage';
import SettingsPage from './pages/SettingsPage';
import PaperDetailPage from './pages/PaperDetailPage';
import { statsAPI, authAPI } from './services/api';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { ToastProvider } from './components/Toast';
import { KeyboardShortcutsHelp } from './components/KeyboardShortcutsHelp';
import './App.css';
import './professional-enhancements.css';

function NavLink({ to, icon: Icon, children, badge }) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link to={to} className={`nav-link ${isActive ? 'active' : ''}`}>
      <Icon size={18} /> {children}
      {badge !== undefined && badge > 0 && (
        <span className="badge">{badge}</span>
      )}
    </Link>
  );
}

function AppContent() {
  const { theme, toggleTheme } = useTheme();
  const [stats, setStats] = useState(null);
  const [authStatus, setAuthStatus] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    loadStats();
    loadAuthStatus();
  }, []);

  // Close sidebar when route changes on mobile
  const location = useLocation();
  useEffect(() => {
    setSidebarOpen(false);
  }, [location]);

  const loadStats = async () => {
    try {
      const response = await statsAPI.get();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadAuthStatus = async () => {
    try {
      const response = await authAPI.getStatus();
      setAuthStatus(response.data);
    } catch (error) {
      console.error('Failed to load auth status:', error);
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(prev => !prev);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="app">
      {/* Mobile Sidebar Toggle */}
      <button
        className="mobile-sidebar-toggle"
        onClick={toggleSidebar}
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? <CloseIcon size={20} /> : <MenuIcon size={20} />}
      </button>

      {/* Sidebar Overlay for Mobile */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'show' : ''}`}
        onClick={closeSidebar}
      />

      {/* Sidebar */}
      <nav className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="logo">
          <h1><span className="logo-icon">LS</span> LitSearch</h1>
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? <MoonIcon size={16} /> : <SunIcon size={16} />}
          </button>
        </div>

        <div className="nav-links">
          <NavLink to="/" icon={SearchIcon}>
            Search
          </NavLink>
          <NavLink to="/library" icon={BookIcon} badge={stats?.total_papers}>
            Library
          </NavLink>
          <NavLink to="/collections" icon={FolderIcon} badge={stats?.total_collections}>
            Collections
          </NavLink>
          <NavLink to="/visualizations" icon={ChartIcon}>
            Visualizations
          </NavLink>
          <NavLink to="/settings" icon={SettingsIcon}>
            Settings
          </NavLink>
        </div>

        <div className="sidebar-footer">
          {authStatus && (
            <div className={`ucsb-status ${authStatus.authenticated ? 'authenticated' : 'not-authenticated'}`}>
              {authStatus.authenticated ? (
                <>
                  <CheckCircleIcon className="status-icon" size={20} />
                  <div className="status-text">
                    <span className="status-title">UCSB Access</span>
                    <span className="status-subtitle">
                      {authStatus.vpn_connected && authStatus.cookie_authenticated
                        ? 'VPN + Cookies'
                        : authStatus.vpn_connected
                        ? 'Via VPN'
                        : 'Via Cookies'}
                    </span>
                  </div>
                </>
              ) : (
                <>
                  <XCircleIcon className="status-icon" size={20} />
                  <div className="status-text">
                    <span className="status-title">UCSB Access</span>
                    <span className="status-subtitle">Not configured</span>
                  </div>
                </>
              )}
            </div>
          )}

          {stats && (
            <div className="sidebar-stats">
              <div className="stat-item">
                <span className="stat-label">Papers:</span>
                <span className="stat-value">{stats.total_papers}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">PDFs:</span>
                <span className="stat-value">{stats.total_pdfs}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Searches:</span>
                <span className="stat-value">{stats.total_searches}</span>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<SearchPage onStatsUpdate={loadStats} />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/paper/:id" element={<PaperDetailPage />} />
          <Route path="/collections" element={<CollectionsPage />} />
          <Route path="/visualizations" element={<VisualizationsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>

      {/* Keyboard Shortcuts Help */}
      <KeyboardShortcutsHelp />
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <Router>
          <AppContent />
        </Router>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
