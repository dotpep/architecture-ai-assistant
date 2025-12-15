/**
 * DownloadButtons Component - Redesigned
 * Modern download buttons with improved styling
 * Requirements: 3.1, 3.2
 */

import React from 'react';

interface DownloadButtonsProps {
  imageUrl?: string;
  markdownUrl?: string;
  chatId: string;
}

const DownloadButtons: React.FC<DownloadButtonsProps> = ({
  imageUrl,
  markdownUrl,
  chatId,
}) => {
  const handleDownload = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!imageUrl && !markdownUrl) {
    return null;
  }

  return (
    <div className="flex items-center gap-2">
      {imageUrl && (
        <button
          onClick={() => handleDownload(imageUrl, `diagram-${chatId}.png`)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600/50 rounded-lg transition-all hover:text-white"
          title="Download PNG"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          PNG
        </button>
      )}
      {markdownUrl && (
        <button
          onClick={() => handleDownload(markdownUrl, `diagram-${chatId}.md`)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600/50 rounded-lg transition-all hover:text-white"
          title="Download Markdown"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          MD
        </button>
      )}
    </div>
  );
};

export default DownloadButtons;
