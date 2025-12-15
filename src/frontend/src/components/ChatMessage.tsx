/**
 * ChatMessage Component - Redesigned
 * Modern message bubbles with improved styling
 * Requirements: 1.2, 1.3
 */

import React from 'react';
import { ChatMessage as ChatMessageType } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
  onRetry?: (message: ChatMessageType) => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onRetry }) => {
  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getDiagramTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      flowchart: 'Flowchart',
      erdiagram: 'ER Diagram',
      sequence: 'Sequence',
      class: 'Class',
      state: 'State',
      architecture: 'Architecture',
      dfd: 'DFD',
    };
    return labels[type] || type;
  };

  return (
    <div className="flex gap-3">
      {/* Avatar */}
      <div className="flex-shrink-0">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-sm font-medium shadow-lg shadow-indigo-500/25">
          U
        </div>
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        {/* User Message */}
        <div className="bg-slate-800/50 rounded-2xl rounded-tl-md px-4 py-3 border border-slate-700/50">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-white">You</span>
            <span className="text-xs text-slate-500">{formatTime(message.timestamp)}</span>
            <span className="px-2 py-0.5 text-xs bg-indigo-500/20 text-indigo-300 rounded-full">
              {getDiagramTypeLabel(message.diagramType)}
            </span>
          </div>
          <p className="text-slate-300 text-sm leading-relaxed">{message.userMessage}</p>
        </div>

        {/* Status Indicators */}
        {message.status === 'pending' && (
          <div className="mt-3 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-slate-700/50 flex items-center justify-center">
              <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
              </svg>
            </div>
            <div className="flex-1 bg-slate-800/30 rounded-2xl rounded-tl-md px-4 py-3 border border-slate-700/30">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
                <span className="text-sm text-slate-400">Generating diagram...</span>
              </div>
            </div>
          </div>
        )}

        {message.status === 'failed' && (
          <div className="mt-3 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-red-500/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="flex-1 bg-red-500/10 rounded-2xl rounded-tl-md px-4 py-3 border border-red-500/20">
              <p className="text-sm text-red-300 mb-2">
                {message.aiResponse || 'Failed to generate diagram'}
              </p>
              {onRetry && (
                <button
                  onClick={() => onRetry(message)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-300 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-colors"
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Retry
                </button>
              )}
            </div>
          </div>
        )}

        {message.status === 'completed' && (
          <div className="mt-3 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
              </svg>
            </div>
            <div className="flex-1 bg-slate-800/30 rounded-2xl rounded-tl-md px-4 py-3 border border-slate-700/30">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-sm text-slate-300">Diagram generated successfully</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
