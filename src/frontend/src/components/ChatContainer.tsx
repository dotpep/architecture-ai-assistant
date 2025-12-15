/**
 * ChatContainer Component - Session-based
 * Modern chat interface with session support
 * Requirements: 1.4, 2.1, 3.3, 4.3
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ChatMessage as ChatMessageType, DiagramType } from '../types';
import { generateDiagram, getSessionMessages, saveChat, updateSessionTitle } from '../services/api';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import DownloadButtons from './DownloadButtons';
import DiagramPreview from './DiagramPreview';
import MermaidCodePreview from './MermaidCodePreview';
import ErrorMessage, { getErrorType } from './ErrorMessage';

interface ChatContainerProps {
  selectedDiagramType: DiagramType;
  currentSessionId: string | null;
  onSessionCreated?: (sessionId: string) => void;
  onFirstMessage?: (sessionId: string, title: string) => void;
}

const ChatContainer: React.FC<ChatContainerProps> = ({ 
  selectedDiagramType, 
  currentSessionId,
  onSessionCreated,
  onFirstMessage
}) => {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // Load messages for current session
  useEffect(() => {
    const loadSessionMessages = async () => {
      if (!currentSessionId) {
        setMessages([]);
        setIsLoadingHistory(false);
        return;
      }

      try {
        setIsLoadingHistory(true);
        setHistoryError(null);
        const response = await getSessionMessages(currentSessionId);
        const sortedMessages = [...response.chats].sort((a, b) => a.timestamp - b.timestamp);
        setMessages(sortedMessages);
      } catch (error) {
        console.error('Failed to load session messages:', error);
        setHistoryError('Failed to load session messages. Please try again.');
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadSessionMessages();
  }, [currentSessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const generateMessageId = (): string => {
    return `msg-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
  };

  const extractSessionTitle = (message: string, maxLength: number = 50): string => {
    if (message.length <= maxLength) return message;
    return message.substring(0, maxLength) + '...';
  };

  const handleSubmit = async (userMessage: string) => {
    // If no current session, notify parent to create one
    if (!currentSessionId) {
      if (onSessionCreated) {
        onSessionCreated(userMessage); // Pass the message to create session with
      }
      return;
    }

    const messageId = generateMessageId();
    const timestamp = Math.floor(Date.now() / 1000);

    const pendingMessage: ChatMessageType = {
      chatId: messageId, // Using messageId as chatId for compatibility
      timestamp,
      userMessage,
      diagramType: selectedDiagramType,
      status: 'pending',
    };

    setMessages((prev) => [...prev, pendingMessage]);
    setIsLoading(true);

    try {
      // Save message to session
      await saveChat({ 
        chatId: messageId, 
        userMessage, 
        diagramType: selectedDiagramType,
        sessionId: currentSessionId 
      });

      // Generate diagram
      const response = await generateDiagram({ 
        userPrompt: userMessage, 
        diagramType: selectedDiagramType,
        sessionId: currentSessionId 
      });

      const completedMessage: ChatMessageType = {
        chatId: response.chatId || messageId,
        timestamp: response.timestamp || timestamp,
        userMessage,
        diagramType: selectedDiagramType,
        mermaidCode: response.mermaidCode,
        imageUrl: response.imageUrl,
        markdownUrl: response.markdownUrl,
        status: 'completed',
      };

      setMessages((prev) => prev.map((msg) => (msg.chatId === messageId ? completedMessage : msg)));

      // Update session title after first message
      if (messages.length === 0 && onFirstMessage) {
        const title = extractSessionTitle(userMessage);
        try {
          await updateSessionTitle(currentSessionId, { title });
          onFirstMessage(currentSessionId, title);
        } catch (error) {
          console.error('Failed to update session title:', error);
        }
      }
    } catch (error) {
      console.error('Failed to generate diagram:', error);
      const errorType = getErrorType(error);
      const errorMessages: Record<string, string> = {
        network: 'Unable to connect. Please check your internet connection.',
        timeout: 'Request timed out. Please try again.',
        invalid: 'Invalid response from server. Please try again.',
        parse: 'Unable to render diagram. The generated code may be invalid.',
        general: 'Failed to generate diagram. Please try again.',
      };

      const failedMessage: ChatMessageType = {
        chatId: messageId,
        timestamp,
        userMessage,
        diagramType: selectedDiagramType,
        aiResponse: error instanceof Error ? error.message : errorMessages[errorType],
        status: 'failed',
      };

      setMessages((prev) => prev.map((msg) => (msg.chatId === messageId ? failedMessage : msg)));
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = async (message: ChatMessageType) => {
    setMessages((prev) => prev.filter((msg) => msg.chatId !== message.chatId));
    await handleSubmit(message.userMessage);
  };

  const renderEmptyState = () => {
    if (!currentSessionId) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-center px-4 py-12">
          <div className="w-20 h-20 mb-6 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center border border-indigo-500/20">
            <svg className="w-10 h-10 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">Start a New Conversation</h3>
          <p className="text-slate-400 max-w-md mb-8">
            Select a session from the sidebar or create a new chat to begin generating diagrams.
          </p>
        </div>
      );
    }

    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-4 py-12">
        <div className="w-20 h-20 mb-6 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center border border-indigo-500/20">
          <svg className="w-10 h-10 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">Create Your First Diagram</h3>
        <p className="text-slate-400 max-w-md mb-8">
          Describe the architecture or system you want to visualize, and AI will generate a professional diagram for you.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full">
          {[
            { icon: '🏗️', text: 'Microservices architecture' },
            { icon: '🗃️', text: 'Database ER diagram' },
            { icon: '🔄', text: 'API sequence flow' },
            { icon: '📦', text: 'Class hierarchy' },
          ].map((example, i) => (
            <button
              key={i}
              onClick={() => handleSubmit(example.text)}
              className="flex items-center gap-3 px-4 py-3 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 hover:border-slate-600/50 rounded-xl text-left transition-all group"
            >
              <span className="text-xl">{example.icon}</span>
              <span className="text-sm text-slate-300 group-hover:text-white">{example.text}</span>
            </button>
          ))}
        </div>
      </div>
    );
  };

  const renderLoadingHistory = () => (
    <div className="flex items-center justify-center h-full">
      <div className="flex flex-col items-center">
        <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center mb-4">
          <svg className="animate-spin h-6 w-6 text-indigo-400" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
        <p className="text-slate-400">Loading session messages...</p>
      </div>
    </div>
  );

  const renderHistoryError = () => (
    <div className="flex items-center justify-center h-full p-4">
      <ErrorMessage
        type="network"
        message={historyError || 'Failed to load session messages'}
        onRetry={() => {
          if (currentSessionId) {
            // Retry loading session messages
            setHistoryError(null);
            setIsLoadingHistory(true);
            getSessionMessages(currentSessionId)
              .then(response => {
                const sortedMessages = [...response.chats].sort((a, b) => a.timestamp - b.timestamp);
                setMessages(sortedMessages);
              })
              .catch(error => {
                console.error('Failed to retry loading session messages:', error);
                setHistoryError('Failed to load session messages. Please try again.');
              })
              .finally(() => {
                setIsLoadingHistory(false);
              });
          }
        }}
        variant="card"
      />
    </div>
  );

  return (
    <div className="flex flex-col h-full bg-slate-900">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {isLoadingHistory ? (
          renderLoadingHistory()
        ) : historyError ? (
          renderHistoryError()
        ) : messages.length === 0 ? (
          renderEmptyState()
        ) : (
          <div className="max-w-4xl mx-auto py-6 px-4 space-y-6">
            {messages.map((message) => (
              <div key={message.chatId} className="space-y-4">
                <ChatMessage message={message} onRetry={handleRetry} />
                
                {message.status === 'completed' && message.mermaidCode && (
                  <div className="ml-12 space-y-4">
                    {/* Diagram Card */}
                    <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 overflow-hidden">
                      <div className="p-4 bg-white rounded-t-xl">
                        <DiagramPreview mermaidCode={message.mermaidCode} imageUrl={message.imageUrl} />
                      </div>
                      <div className="p-4 border-t border-slate-700/50">
                        <div className="flex items-center justify-between">
                          <MermaidCodePreview code={message.mermaidCode} />
                          <DownloadButtons
                            imageUrl={message.imageUrl}
                            markdownUrl={message.markdownUrl}
                            chatId={message.chatId}
                          />
                        </div>
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
      <div className="flex-shrink-0 border-t border-slate-700/50 bg-slate-800/30">
        <div className="max-w-4xl mx-auto">
          <ChatInput 
            onSubmit={handleSubmit} 
            isLoading={isLoading} 
            disabled={isLoadingHistory || !currentSessionId} 
            placeholder={!currentSessionId ? "Select a session or create a new chat to start..." : undefined}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatContainer;
