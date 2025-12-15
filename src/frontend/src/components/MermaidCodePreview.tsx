/**
 * MermaidCodePreview Component
 * Displays Mermaid code in a syntax-highlighted code block
 * Requirements: 2.2
 */

import React, { useState } from 'react';

interface MermaidCodePreviewProps {
  code: string;
  title?: string;
  showLineNumbers?: boolean;
}

/**
 * MermaidCodePreview Component
 * Renders Mermaid code with syntax highlighting and copy functionality
 */
const MermaidCodePreview: React.FC<MermaidCodePreviewProps> = ({
  code,
  title = 'mermaid',
  showLineNumbers = false,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  const lines = code.split('\n');

  return (
    <div className="bg-gray-900 rounded-lg overflow-hidden shadow-sm" data-testid="mermaid-code-preview">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <span className="text-xs text-gray-400 font-mono">{title}</span>
        <button
          onClick={handleCopy}
          className="flex items-center space-x-1 text-xs text-gray-400 hover:text-white transition-colors"
          title="Copy code"
          aria-label="Copy code to clipboard"
        >
          {copied ? (
            <>
              <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-green-400">Copied!</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code Block */}
      <div className="overflow-x-auto">
        <pre className="p-4" data-testid="mermaid-code-block">
          {showLineNumbers ? (
            <code className="text-sm font-mono">
              {lines.map((line, index) => (
                <div key={index} className="flex">
                  <span className="text-gray-600 select-none w-8 text-right pr-4">
                    {index + 1}
                  </span>
                  <span className="text-green-400 whitespace-pre">{line}</span>
                </div>
              ))}
            </code>
          ) : (
            <code className="text-sm text-green-400 font-mono whitespace-pre">
              {code}
            </code>
          )}
        </pre>
      </div>
    </div>
  );
};

export default MermaidCodePreview;
