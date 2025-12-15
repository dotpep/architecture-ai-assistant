/**
 * ChatInput Component - Redesigned
 * Modern input with improved styling
 * Requirements: 1.2, 1.3
 */

import React, { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSubmit: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSubmit,
  isLoading = false,
  placeholder = 'Describe the diagram you want to create...',
  disabled = false,
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedMessage = message.trim();
    if (trimmedMessage && !isLoading && !disabled) {
      onSubmit(trimmedMessage);
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isSubmitDisabled = !message.trim() || isLoading || disabled;

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="p-4">
        <div className="flex items-end gap-3 bg-slate-800/50 border border-slate-700/50 rounded-2xl p-2 focus-within:border-indigo-500/50 focus-within:ring-2 focus-within:ring-indigo-500/20 transition-all">
          {/* Text Input */}
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={isLoading || disabled}
              rows={1}
              className={`
                w-full px-3 py-2.5 
                bg-transparent border-0
                resize-none overflow-hidden
                focus:outline-none focus:ring-0
                ${(isLoading || disabled) ? 'cursor-not-allowed opacity-50' : ''}
                text-white placeholder-slate-500
                text-sm
              `}
              aria-label="Message input"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitDisabled}
            className={`
              flex items-center justify-center
              p-3 rounded-xl
              transition-all duration-200
              ${isSubmitDisabled
                ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40'
              }
            `}
            aria-label={isLoading ? 'Generating diagram...' : 'Send message'}
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>

        {/* Helper text */}
        <p className="mt-2 text-xs text-slate-500 text-center">
          Press <kbd className="px-1.5 py-0.5 bg-slate-700/50 rounded text-slate-400">Enter</kbd> to send, <kbd className="px-1.5 py-0.5 bg-slate-700/50 rounded text-slate-400">Shift+Enter</kbd> for new line
        </p>
      </div>
    </form>
  );
};

export default ChatInput;
