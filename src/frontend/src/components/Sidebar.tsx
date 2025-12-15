/**
 * Sidebar Component
 * Session history and new chat functionality
 * Requirements: 3.1, 3.2, 3.3, 3.4
 */

import React from 'react';
import { Session } from '../types';
import { groupSessionsByDate } from '../utils';

interface SidebarProps {
  isOpen: boolean;
  onNewChat: () => void;
  onSelectSession: (sessionId: string) => void;
  currentSessionId: string | null;
  sessions: Session[];
  isLoading?: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onNewChat,
  onSelectSession,
  currentSessionId,
  sessions,
  isLoading = false,
}) => {
  // Group sessions by date using utility function
  const groupedSessions = React.useMemo(() => {
    return groupSessionsByDate(sessions);
  }, [sessions]);

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const getDiagramIcon = (type: string) => {
    switch (type) {
      case 'flowchart':
        return '📊';
      case 'erdiagram':
        return '🗃️';
      case 'sequence':
        return '🔄';
      case 'class':
        return '📦';
      case 'state':
        return '🔀';
      case 'architecture':
        return '🏗️';
      case 'dfd':
        return '📈';
      default:
        return '📋';
    }
  };

  return (
    <aside
      className={`
        ${isOpen ? 'w-72' : 'w-0'} 
        flex-shrink-0 bg-slate-800/50 border-r border-slate-700/50 
        transition-all duration-300 ease-in-out overflow-hidden
        flex flex-col
      `}
    >
      <div className="flex flex-col h-full w-72">
        {/* New Chat Button */}
        <div className="p-4">
          <button
            onClick={onNewChat}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl font-medium transition-all shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Session History */}
        <div className="flex-1 overflow-y-auto px-3 pb-4">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-700/50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500"></div>
              </div>
              <p className="text-sm text-slate-500">Loading sessions...</p>
            </div>
          ) : Object.keys(groupedSessions).length === 0 ? (
            <div className="text-center py-8">
              <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-700/50 flex items-center justify-center">
                <svg className="w-6 h-6 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <p className="text-sm text-slate-500">No sessions yet</p>
              <p className="text-xs text-slate-600 mt-1">Start a new conversation!</p>
            </div>
          ) : (
            Object.entries(groupedSessions).map(([group, sessionList]) => (
              <div key={group} className="mb-4">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-2 mb-2">
                  {group}
                </h3>
                <div className="space-y-1">
                  {sessionList.map((session) => (
                    <button
                      key={session.sessionId}
                      onClick={() => onSelectSession(session.sessionId)}
                      className={`
                        w-full text-left px-3 py-2.5 rounded-lg transition-all group
                        ${currentSessionId === session.sessionId
                          ? 'bg-indigo-600/20 border border-indigo-500/30 text-white'
                          : 'hover:bg-slate-700/50 text-slate-300 hover:text-white'
                        }
                      `}
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-base flex-shrink-0 mt-0.5">
                          {getDiagramIcon(session.diagramType)}
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">
                            {truncateText(session.title, 30)}
                          </p>
                          <p className="text-xs text-slate-500 mt-0.5">
                            {new Date(session.createdAt * 1000).toLocaleDateString(undefined, { 
                              month: 'short', 
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-700/50">
          <div className="flex items-center gap-3 text-slate-400">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-sm font-medium">
              AI
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-300">Architecture AI</p>
              <p className="text-xs text-slate-500">v1.0.0</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
