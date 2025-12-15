/**
 * ChatMessage Component
 * Displays user and AI messages with proper styling
 * Requirements: 1.3, 2.2
 */

import React from 'react';
import { ChatMessage as ChatMessageType, DiagramType } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
  onRetry?: (message: ChatMessageType) => void;
}

/**
 * Get display label for diagram type
 */
const getDiagramTypeLabel = (type: DiagramType): string => {
  const labels: Record<DiagramType, string> = {
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

/**
 * Format timestamp to readable string
 */
const formatTimestamp = (timestamp: number): string => {
  const date = new Date(timestamp * 1000);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

/**
 * User Message Component
 */
const UserMessage: React.FC<{ message: string; diagramType: DiagramType; timestamp: number }> = ({
  message,
  diagramType,
  timestamp,
}) => {
  return (
    <div className="flex justify-end mb-4">
      <div className="max-w-[80%] lg:max-w-[60%]">
        <div className="bg-indigo-600 text-white rounded-2xl rounded-br-md px-4 py-3 shadow-sm">
          <p className="text-sm whitespace-pre-wrap break-words">{message}</p>
        </div>
        <div className="flex items-center justify-end mt-1 space-x-2">
          <span className="text-xs text-gray-500">
            {getDiagramTypeLabel(diagramType)}
          </span>
          <span className="text-xs text-gray-400">•</span>
          <span className="text-xs text-gray-400">
            {formatTimestamp(timestamp)}
          </span>
        </div>
      </div>
      {/* User Avatar */}
      <div className="flex-shrink-0 ml-3">
        <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
      </div>
    </div>
  );
};

/**
 * AI Message Component
 */
const AIMessage: React.FC<{
  message: ChatMessageType;
  onRetry?: (message: ChatMessageType) => void;
}> = ({ message, onRetry }) => {
  const { status, mermaidCode, aiResponse, timestamp } = message;

  return (
    <div className="flex justify-start mb-4">
      {/* AI Avatar */}
      <div className="flex-shrink-0 mr-3">
        <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
      </div>
      <div className="max-w-[80%] lg:max-w-[70%]">
        {/* Status: Pending */}
        {status === 'pending' && (
          <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <span className="text-sm text-gray-500">Generating diagram...</span>
            </div>
          </div>
        )}

        {/* Status: Failed */}
        {status === 'failed' && (
          <div className="bg-red-50 border border-red-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
            <div className="flex items-start space-x-2">
              <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-sm text-red-700">
                  {aiResponse || 'Failed to generate diagram. Please try again.'}
                </p>
                {onRetry && (
                  <button
                    onClick={() => onRetry(message)}
                    className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
                  >
                    Retry
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Status: Completed */}
        {status === 'completed' && (
          <div className="space-y-3">
            {/* AI Response Text */}
            {aiResponse && (
              <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                <p className="text-sm text-gray-800 whitespace-pre-wrap break-words">
                  {aiResponse}
                </p>
              </div>
            )}

            {/* Mermaid Code Block */}
            {mermaidCode && (
              <div className="bg-gray-900 rounded-lg overflow-hidden shadow-sm">
                <div className="flex items-center justify-between px-4 py-2 bg-gray-800">
                  <span className="text-xs text-gray-400 font-mono">mermaid</span>
                  <button
                    onClick={() => navigator.clipboard.writeText(mermaidCode)}
                    className="text-xs text-gray-400 hover:text-white transition-colors"
                    title="Copy code"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
                <pre className="p-4 overflow-x-auto">
                  <code className="text-sm text-green-400 font-mono whitespace-pre">
                    {mermaidCode}
                  </code>
                </pre>
              </div>
            )}
          </div>
        )}

        {/* Timestamp */}
        <div className="mt-1">
          <span className="text-xs text-gray-400">
            {formatTimestamp(timestamp)}
          </span>
        </div>
      </div>
    </div>
  );
};

/**
 * Main ChatMessage Component
 * Renders either UserMessage or AIMessage based on context
 */
const ChatMessage: React.FC<ChatMessageProps> = ({ message, onRetry }) => {
  return (
    <div className="px-4">
      {/* User's message */}
      <UserMessage
        message={message.userMessage}
        diagramType={message.diagramType}
        timestamp={message.timestamp}
      />
      {/* AI's response */}
      <AIMessage message={message} onRetry={onRetry} />
    </div>
  );
};

export default ChatMessage;

/**
 * Export individual components for flexibility
 */
export { UserMessage, AIMessage };
