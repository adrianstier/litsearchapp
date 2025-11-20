import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
  FaSearch, FaBook, FaFolderOpen, FaChartLine, FaCog,
  FaCheckCircle, FaTimesCircle, FaSun, FaMoon, FaBars, FaTimes
} from 'react-icons/fa';
import SearchPage from './pages/SearchPage';
import LibraryPage from './pages/LibraryPage';
import CollectionsPage from './pages/CollectionsPage';
import VisualizationsPage from './pages/VisualizationsPage';
import SettingsPage from './pages/SettingsPage';
import { statsAPI, authAPI } from './services/api';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { ToastProvider } from './components/Toast';
import { KeyboardShortcutsHelp } from './components/KeyboardShortcutsHelp';

function NavLink({ to, icon: Icon, children, badge }) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={`
        flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium
        transition-all duration-200 relative
        ${isActive
          ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400 font-semibold border-r-4 border-primary-600'
          : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
        }
      `}
    >
      <Icon className="w-5 h-5" />
      <span className="flex-1">{children}</span>
      {badge !== undefined && badge > 0 && (
        <span className="badge-primary text-xs px-2 py-0.5">
          {badge}
        </span>
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
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 overflow-hidden">
      {/* Mobile Sidebar Toggle */}
      <button
        className="fixed top-4 left-4 z-50 md:hidden bg-white dark:bg-slate-800 p-3 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
        onClick={toggleSidebar}
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? <FaTimes className="w-5 h-5" /> : <FaBars className="w-5 h-5" />}
      </button>

      {/* Sidebar Overlay for Mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 md:hidden transition-opacity"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <nav className={`
        fixed md:static inset-y-0 left-0 z-40
        w-64 h-screen
        bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800
        flex flex-col
        transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        {/* Logo and Theme Toggle */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-800">
          <h1 className="text-xl font-bold text-gradient flex items-center gap-2">
            <span>📚</span>
            <span>LitSearch</span>
          </h1>
          <button
            className="p-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? <FaMoon className="w-5 h-5" /> : <FaSun className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation Links */}
        <div className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-1">
          <NavLink to="/" icon={FaSearch}>
            Search
          </NavLink>
          <NavLink to="/library" icon={FaBook} badge={stats?.total_papers}>
            Library
          </NavLink>
          <NavLink to="/collections" icon={FaFolderOpen} badge={stats?.total_collections}>
            Collections
          </NavLink>
          <NavLink to="/visualizations" icon={FaChartLine}>
            Visualizations
          </NavLink>
          <NavLink to="/settings" icon={FaCog}>
            Settings
          </NavLink>
        </div>

        {/* Sidebar Footer */}
        <div className="border-t border-slate-200 dark:border-slate-800 p-4 space-y-4">
          {/* UCSB Status */}
          {authStatus && (
            <div className={`
              flex items-start gap-3 p-3 rounded-lg
              ${authStatus.authenticated
                ? 'bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800'
                : 'bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700'
              }
            `}>
              {authStatus.authenticated ? (
                <FaCheckCircle className="w-5 h-5 text-success-600 dark:text-success-400 flex-shrink-0 mt-0.5" />
              ) : (
                <FaTimesCircle className="w-5 h-5 text-slate-400 dark:text-slate-500 flex-shrink-0 mt-0.5" />
              )}
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-semibold ${authStatus.authenticated ? 'text-success-900 dark:text-success-100' : 'text-slate-700 dark:text-slate-300'}`}>
                  UCSB Access
                </p>
                <p className={`text-xs ${authStatus.authenticated ? 'text-success-700 dark:text-success-300' : 'text-slate-500 dark:text-slate-400'}`}>
                  {authStatus.authenticated ? 'Enabled' : 'Not configured'}
                </p>
              </div>
            </div>
          )}

          {/* Statistics */}
          {stats && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-400">Papers:</span>
                <span className="font-semibold text-slate-900 dark:text-slate-100">{stats.total_papers}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-400">PDFs:</span>
                <span className="font-semibold text-slate-900 dark:text-slate-100">{stats.total_pdfs}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-400">Searches:</span>
                <span className="font-semibold text-slate-900 dark:text-slate-100">{stats.total_searches}</span>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="min-h-full p-4 md:p-8">
          <Routes>
            <Route path="/" element={<SearchPage onStatsUpdate={loadStats} />} />
            <Route path="/library" element={<LibraryPage />} />
            <Route path="/collections" element={<CollectionsPage />} />
            <Route path="/visualizations" element={<VisualizationsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </div>
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
