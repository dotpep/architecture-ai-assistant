/**
 * Main App Component
 * Composes Header, DiagramTypeSelector, and ChatContainer
 * Manages global state for diagram type selection
 * Requirements: 1.1, 1.4
 */

import React, { useState, useCallback } from 'react';
import { DiagramType } from './types';
import { Header, DiagramTypeSelector, ChatContainer } from './components';
import './App.css';

/**
 * Error boundary state interface
 */
interface ErrorState {
  hasError: boolean;
  error: Error | null;
  errorInfo: string | null;
}

/**
 * Error Boundary Component for catching React errors
 * Requirements: 1.5
 */
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; onReset: () => void },
  ErrorState
> {
  constructor(props: { children: React.ReactNode; onReset: () => void }) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('App Error:', error, errorInfo);
    this.setState({ errorInfo: errorInfo.componentStack || null });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    this.props.onReset();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
              <svg
                className="w-8 h-8 text-red-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Something went wrong
            </h2>
            <p className="text-gray-600 mb-4">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <button
              onClick={this.handleReset}
              className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Main App Component
 */
const App: React.FC = () => {
  // Global state for diagram type selection
  const [selectedDiagramType, setSelectedDiagramType] = useState<DiagramType>('flowchart');
  const [key, setKey] = useState(0);

  /**
   * Handle diagram type change
   * Requirements: 1.4
   */
  const handleDiagramTypeChange = useCallback((type: DiagramType) => {
    setSelectedDiagramType(type);
  }, []);

  /**
   * Reset app state on error recovery
   */
  const handleErrorReset = useCallback(() => {
    setKey((prev) => prev + 1);
    setSelectedDiagramType('flowchart');
  }, []);

  return (
    <ErrorBoundary onReset={handleErrorReset}>
      <div key={key} className="min-h-screen bg-gray-50 flex flex-col">
        {/* Header */}
        <Header />

        {/* Main Content */}
        <main className="flex-1 flex flex-col max-w-7xl w-full mx-auto">
          {/* Diagram Type Selector Bar */}
          <div className="bg-white border-b border-gray-200 px-4 py-3 sm:px-6">
            <div className="flex items-center justify-between">
              <DiagramTypeSelector
                selectedType={selectedDiagramType}
                onTypeChange={handleDiagramTypeChange}
              />
            </div>
          </div>

          {/* Chat Container */}
          <div className="flex-1 overflow-hidden">
            <ChatContainer selectedDiagramType={selectedDiagramType} />
          </div>
        </main>
      </div>
    </ErrorBoundary>
  );
};

export default App;
