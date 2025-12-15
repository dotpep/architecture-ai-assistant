/**
 * ChatContainer Component
 * Composes ChatMessages and ChatInput components
 * Manages chat state and API interactions
 * Requirements: 1.1, 1.2, 1.3
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ChatMessage as ChatMessageType, DiagramType } from '../types';
import { generateDiagram, getChatHistory, saveChat } from '../services/api';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import DownloadButtons from './DownloadButtons';
import DiagramRenderer from './DiagramRenderer';

interface ChatContainerProps {
  selectedDiagramType: DiagramType;
}

const ChatContainer: React.FC<ChatContainerProps> = ({ selectedDiagramType }) => {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /**
   * Scroll to bottom of messages
   */
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  /**
   * Load chat history on component mount
   * Requirements: 4.2, 4.3
   */
  useEffect(() => {
    const loadHistory = async () => {
      try {
        setIsLoadingHistory(true);
        setHistoryError(null);
        const response = await getChatHistory({ limit: 50 });
        
        // Sort messages by timestamp (oldest first for display)
        const sortedChats = [...response.chats].sort(
          (a, b) => a.timestamp - b.timestamp
        );
        
        setMessages(sortedChats);
      } catch (error) {
        console.error('Failed to load chat history:', error);
        setHistoryError('Failed to load chat history. Please refresh the page.');
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadHistory();
  }, []);

  /**
   * Scroll to bottom when messages change
   */
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  /**
   * Generate a unique chat ID
   */
  const generateChatId = (): string => {
    return `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  /**
   * Handle message submission
   * Requirements: 1.2, 1.3
   */
  const handleSubmit = async (userMessage: string) => {
    const chatId = generateChatId();
    const timestamp = Math.floor(Date.now() / 1000);

    // Create pending message
    const pendingMessage: ChatMessageType = {
      chatId,
      timestamp,
      userMessage,
      diagramType: selectedDiagramType,
      status: 'pending',
    };

    // Add pending message to state
    setMessages((prev) => [...prev, pendingMessage]);
    setIsLoading(true);

    try {
      // Save the user message first
      await saveChat({
        chatId,
        userMessage,
        diagramType: selectedDiagramType,
      });

      // Generate diagram
      const response = await generateDiagram({
        userPrompt: userMessage,
        diagramType: selectedDiagramType,
      });

      // Update message with response
      const completedMessage: ChatMessageType = {
        chatId: response.chatId || chatId,
        timestamp: response.timestamp || timestamp,
        userMessage,
        diagramType: selectedDiagramType,
        mermaidCode: response.mermaidCode,
        imageUrl: response.imageUrl,
        markdownUrl: response.markdownUrl,
        status: 'completed',
      };

      setMessages((prev) =>
        prev.map((msg) =>
          msg.chatId === chatId ? completedMessage : msg
        )
      );
    } catch (error) {
      console.error('Failed to generate diagram:', error);
      
      // Update message with error status
      const failedMessage: ChatMessageType = {
        chatId,
        timestamp,
        userMessage,
        diagramType: selectedDiagramType,
        aiResponse: error instanceof Error ? error.message : 'Failed to generate diagram',
        status: 'failed',
      };

      setMessages((prev) =>
        prev.map((msg) =>
          msg.chatId === chatId ? failedMessage : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle retry for failed messages
   * Requirements: 1.5
   */
  const handleRetry = async (message: ChatMessageType) => {
    // Remove the failed message
    setMessages((prev) => prev.filter((msg) => msg.chatId !== message.chatId));
    
    // Resubmit the message
    await handleSubmit(message.userMessage);
  };

  /**
   * Render empty state
   */
  const renderEmptyState = () => (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <div className="w-16 h-16 mb-4 rounded-full bg-indigo-100 flex items-center justify-center">
        <svg 
          className="w-8 h-8 text-indigo-600" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" 
          />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        Start Creating Diagrams
      </h3>
      <p className="text-sm text-gray-500 max-w-sm">
        Describe the architecture or system you want to visualize, and I'll generate a diagram for you.
      </p>
    </div>
  );

  /**
   * Render loading history state
   */
  const renderLoadingHistory = () => (
    <div className="flex items-center justify-center h-full">
      <div className="flex flex-col items-center">
        <svg 
          className="animate-spin h-8 w-8 text-indigo-600 mb-3" 
          fill="none" 
          viewBox="0 0 24 24"
        >
          <circle 
            className="opacity-25" 
            cx="12" 
            cy="12" 
            r="10" 
            stroke="currentColor" 
            strokeWidth="4"
          />
          <path 
            className="opacity-75" 
            fill="currentColor" 
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        <p className="text-sm text-gray-500">Loading chat history...</p>
      </div>
    </div>
  );

  /**
   * Render history error state
   */
  const renderHistoryError = () => (
    <div className="flex items-center justify-center h-full">
      <div className="flex flex-col items-center text-center px-4">
        <div className="w-12 h-12 mb-3 rounded-full bg-red-100 flex items-center justify-center">
          <svg 
            className="w-6 h-6 text-red-600" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
            />
          </svg>
        </div>
        <p className="text-sm text-red-600 mb-2">{historyError}</p>
        <button
          onClick={() => window.location.reload()}
          className="text-sm text-indigo-600 hover:text-indigo-800 underline"
        >
          Refresh page
        </button>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto py-4">
        {isLoadingHistory ? (
          renderLoadingHistory()
        ) : historyError ? (
          renderHistoryError()
        ) : messages.length === 0 ? (
          renderEmptyState()
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.chatId} className="space-y-3">
                <ChatMessage message={message} onRetry={handleRetry} />
                
                {/* Render diagram if completed with mermaid code */}
                {message.status === 'completed' && message.mermaidCode && (
                  <div className="px-4 ml-11">
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <DiagramRenderer mermaidCode={message.mermaidCode} />
                      
                      {/* Download buttons */}
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <DownloadButtons
                          imageUrl={message.imageUrl}
                          markdownUrl={message.markdownUrl}
                          chatId={message.chatId}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0">
        <ChatInput
          onSubmit={handleSubmit}
          isLoading={isLoading}
          disabled={isLoadingHistory}
        />
      </div>
    </div>
  );
};

export default ChatContainer;
