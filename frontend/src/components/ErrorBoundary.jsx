import { Component } from 'react';
import { FaExclamationTriangle, FaRedo, FaHome } from 'react-icons/fa';
import './ErrorBoundary.css';

/**
 * Error Boundary component to catch JavaScript errors in child components
 * and display a fallback UI instead of crashing the whole app.
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to console in development
    console.error('Error caught by ErrorBoundary:', error);
    console.error('Error info:', errorInfo);

    this.setState({
      error,
      errorInfo,
    });

    // In production, you might want to log to an error reporting service
    // logErrorToService(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // Render fallback UI
      return (
        <div className="error-boundary">
          <div className="error-boundary-content">
            <FaExclamationTriangle className="error-icon" />
            <h1>Something went wrong</h1>
            <p className="error-message">
              {this.props.fallbackMessage ||
                'An unexpected error occurred. Please try again or return to the home page.'}
            </p>

            {/* Show error details in development */}
            {import.meta.env.DEV && this.state.error && (
              <details className="error-details">
                <summary>Error Details (Development Only)</summary>
                <pre>{this.state.error.toString()}</pre>
                {this.state.errorInfo && (
                  <pre>{this.state.errorInfo.componentStack}</pre>
                )}
              </details>
            )}

            <div className="error-actions">
              <button onClick={this.handleRetry} className="retry-button">
                <FaRedo /> Try Again
              </button>
              <button onClick={this.handleGoHome} className="home-button">
                <FaHome /> Go to Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Functional wrapper for creating error boundaries with custom fallback
 */
export function withErrorBoundary(WrappedComponent, fallbackMessage) {
  return function ErrorBoundaryWrapper(props) {
    return (
      <ErrorBoundary fallbackMessage={fallbackMessage}>
        <WrappedComponent {...props} />
      </ErrorBoundary>
    );
  };
}

export default ErrorBoundary;
