import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="terminal">
          <div className="terminal-header">
            <div className="terminal-dot terminal-dot-red"></div>
            <div className="terminal-dot terminal-dot-yellow"></div>
            <div className="terminal-dot terminal-dot-green"></div>
            <span className="text-red-400 font-semibold">Application Error</span>
          </div>
          <div className="p-4 text-red-300">
            <h2 className="text-xl font-bold mb-2">Something went wrong!</h2>
            <p className="mb-4">The application encountered an error and needs to be reloaded.</p>
            <details className="mb-4">
              <summary className="cursor-pointer text-blue-400 hover:text-blue-300">
                Error Details
              </summary>
              <pre className="mt-2 p-2 bg-gray-800 rounded text-xs overflow-auto">
                {this.state.error?.toString()}
              </pre>
            </details>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
