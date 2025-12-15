/**
 * Main App Component - Session-based UI
 * Modern layout with sidebar, pinned header, and session management
 * Requirements: 1.1, 1.2, 1.3, 1.4
 */

import React, { useState, useCallback } from 'react';
import { DiagramType } from './types';
import { Sidebar, Header, ChatContainer } from './components';
import { useSessionState } from './hooks/useSessionState';
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
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-slate-800 rounded-2xl shadow-2xl p-8 text-center border border-slate-700">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
              <svg className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Something went wrong</h2>
            <p className="text-slate-400 mb-6">{this.state.error?.message || 'An unexpected error occurred'}</p>
            <button onClick={this.handleReset} className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-500 transition-all font-medium">
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
  const [selectedDiagramType, setSelectedDiagramType] = useState<DiagramType>('flowchart');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [key, setKey] = useState(0);

  // Session state management
  const {
    currentSessionId,
    sessions,
    isLoadingSessions,
    createNewSession,
    selectSession,
    loadSessions,
    updateSessionTitle,
    clearError
  } = useSessionState();

  const handleDiagramTypeChange = useCallback((type: DiagramType) => {
    setSelectedDiagramType(type);
  }, []);

  /**
   * Handle new chat creation
   * Requirements: 1.1, 1.2, 1.3 - Create new session and set as current
   */
  const handleNewChat = useCallback(async () => {
    try {
      clearError();
      await createNewSession();
      setKey((prev) => prev + 1); // Force ChatContainer re-render
    } catch (error) {
      console.error('Failed to create new session:', error);
      // Error is handled by useSessionState hook
    }
  }, [createNewSession, clearError]);

  /**
   * Handle session selection
   * Requirements: 1.3 - Session selection and navigation
   */
  const handleSelectSession = useCallback((sessionId: string) => {
    selectSession(sessionId);
  }, [selectSession]);

  /**
   * Handle session creation from ChatContainer
   * Requirements: 1.2 - Create session when first message is sent
   */
  const handleSessionCreated = useCallback(async (_firstMessage: string) => {
    try {
      clearError();
      await createNewSession();
    } catch (error) {
      console.error('Failed to create session from chat:', error);
      // Error is handled by useSessionState hook
    }
  }, [createNewSession, clearError]);

  /**
   * Handle first message in session (update title)
   * Requirements: 4.3 - Update session title after first message
   */
  const handleFirstMessage = useCallback(async (sessionId: string, title: string) => {
    try {
      await updateSessionTitle(sessionId, title);
      // Reload sessions to get updated title
      await loadSessions();
    } catch (error) {
      console.error('Failed to update session title:', error);
      // Error is handled by useSessionState hook
    }
  }, [updateSessionTitle, loadSessions]);

  const handleErrorReset = useCallback(() => {
    setKey((prev) => prev + 1);
    setSelectedDiagramType('flowchart');
    clearError();
  }, [clearError]);

  const handleToggleSidebar = useCallback(() => {
    setSidebarOpen((prev) => !prev);
  }, []);

  return (
    <ErrorBoundary onReset={handleErrorReset}>
      <div className="h-screen flex flex-col bg-slate-900 overflow-hidden">
        {/* Pinned Header */}
        <Header 
          onToggleSidebar={handleToggleSidebar} 
          sidebarOpen={sidebarOpen}
          selectedDiagramType={selectedDiagramType}
          onDiagramTypeChange={handleDiagramTypeChange}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <Sidebar
            isOpen={sidebarOpen}
            onNewChat={handleNewChat}
            onSelectSession={handleSelectSession}
            currentSessionId={currentSessionId}
            sessions={sessions}
            isLoading={isLoadingSessions}
          />

          {/* Chat Area */}
          <main className="flex-1 flex flex-col overflow-hidden">
            <ChatContainer
              key={key}
              selectedDiagramType={selectedDiagramType}
              currentSessionId={currentSessionId}
              onSessionCreated={handleSessionCreated}
              onFirstMessage={handleFirstMessage}
            />
          </main>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default App;
