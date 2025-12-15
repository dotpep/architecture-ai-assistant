/**
 * Session State Management Hook
 * Manages session list, current session, and session operations
 * Requirements: 1.2, 1.3, 3.3
 */

import { useState, useCallback, useEffect } from 'react';
import { Session, SessionListResponse, CreateSessionResponse } from '../types';
import { 
  createSession, 
  getSessions, 
  updateSessionTitle, 
  deleteSession 
} from '../services/api';

/**
 * Session state interface
 */
export interface SessionState {
  currentSessionId: string | null;
  sessions: Session[];
  isCreatingSession: boolean;
  isLoadingSessions: boolean;
  error: string | null;
}

/**
 * Session actions interface
 */
export interface SessionActions {
  createNewSession(): Promise<string>;
  selectSession(sessionId: string): void;
  loadSessions(): Promise<void>;
  updateSessionTitle(sessionId: string, title: string): Promise<void>;
  deleteSession(sessionId: string): Promise<void>;
  clearError(): void;
}

/**
 * Combined hook return type
 */
export interface UseSessionStateReturn extends SessionState, SessionActions {}

/**
 * Session state management hook
 * 
 * Provides centralized session state management including:
 * - Session list loading and caching
 * - Current session tracking
 * - Session creation with automatic selection
 * - Session operations (update title, delete)
 * - Error handling and loading states
 * 
 * @returns Session state and actions
 */
export const useSessionState = (): UseSessionStateReturn => {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load sessions from API
   * Requirements: 3.3 - Load and display sessions
   */
  const loadSessions = useCallback(async (): Promise<void> => {
    try {
      setIsLoadingSessions(true);
      setError(null);
      
      const response: SessionListResponse = await getSessions();
      setSessions(response.sessions);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load sessions';
      setError(errorMessage);
      console.error('Failed to load sessions:', err);
    } finally {
      setIsLoadingSessions(false);
    }
  }, []);

  /**
   * Create a new session
   * Requirements: 1.2, 1.3 - Create session and set as current
   * 
   * @returns Promise resolving to the new session ID
   */
  const createNewSession = useCallback(async (): Promise<string> => {
    try {
      setIsCreatingSession(true);
      setError(null);

      const newSession: CreateSessionResponse = await createSession();
      
      // Add new session to the beginning of the list
      setSessions(prevSessions => [newSession, ...prevSessions]);
      
      // Set as current session
      setCurrentSessionId(newSession.sessionId);
      
      return newSession.sessionId;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create session';
      setError(errorMessage);
      console.error('Failed to create session:', err);
      throw err;
    } finally {
      setIsCreatingSession(false);
    }
  }, []);

  /**
   * Select a session as current
   * Requirements: 3.3 - Session selection
   * 
   * @param sessionId - The session ID to select
   */
  const selectSession = useCallback((sessionId: string): void => {
    setCurrentSessionId(sessionId);
    setError(null);
  }, []);

  /**
   * Update session title
   * Requirements: 1.2 - Session title management
   * 
   * @param sessionId - The session ID to update
   * @param title - The new title
   */
  const updateSessionTitleAction = useCallback(async (
    sessionId: string, 
    title: string
  ): Promise<void> => {
    try {
      setError(null);
      
      const updatedSession = await updateSessionTitle(sessionId, { title });
      
      // Update session in local state
      setSessions(prevSessions => 
        prevSessions.map(session => 
          session.sessionId === sessionId 
            ? { ...session, title: updatedSession.title, updatedAt: updatedSession.updatedAt }
            : session
        )
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update session title';
      setError(errorMessage);
      console.error('Failed to update session title:', err);
      throw err;
    }
  }, []);

  /**
   * Delete a session
   * Requirements: 3.3 - Session management
   * 
   * @param sessionId - The session ID to delete
   */
  const deleteSessionAction = useCallback(async (sessionId: string): Promise<void> => {
    try {
      setError(null);
      
      await deleteSession(sessionId);
      
      // Remove session from local state
      setSessions(prevSessions => 
        prevSessions.filter(session => session.sessionId !== sessionId)
      );
      
      // Clear current session if it was deleted
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete session';
      setError(errorMessage);
      console.error('Failed to delete session:', err);
      throw err;
    }
  }, [currentSessionId]);

  /**
   * Clear error state
   */
  const clearError = useCallback((): void => {
    setError(null);
  }, []);

  /**
   * Load sessions on mount
   */
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  return {
    // State
    currentSessionId,
    sessions,
    isCreatingSession,
    isLoadingSessions,
    error,
    
    // Actions
    createNewSession,
    selectSession,
    loadSessions,
    updateSessionTitle: updateSessionTitleAction,
    deleteSession: deleteSessionAction,
    clearError,
  };
};

export default useSessionState;