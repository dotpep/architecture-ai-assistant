/**
 * DownloadButtons Component
 * Provides PNG and markdown download buttons for generated diagrams
 * Requirements: 3.3, 3.4, 3.5
 */

import React, { useState } from 'react';

interface DownloadButtonsProps {
  imageUrl?: string;
  markdownUrl?: string;
  chatId: string;
  disabled?: boolean;
}

/**
 * Trigger file download from URL
 * @param url - The URL to download from
 * @param filename - The filename for the downloaded file
 */
const downloadFile = async (url: string, filename: string): Promise<void> => {
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': '*/*',
      },
      // Disable CORS mode to allow CloudFront to serve the file
      mode: 'cors',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to download: ${response.statusText}`);
    }
    
    const blob = await response.blob();
    
    // Validate that we got the expected content type
    const contentType = response.headers.get('content-type') || '';
    console.log(`Downloaded content-type: ${contentType}, size: ${blob.size} bytes`);
    
    // Check if we got HTML instead of the expected file
    if (blob.type === 'text/html' || contentType.includes('text/html')) {
      console.warn('Warning: Received HTML content instead of file. This may indicate a CloudFront caching issue.');
    }
    
    const blobUrl = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.URL.revokeObjectURL(blobUrl);
  } catch (error) {
    console.error('Download failed:', error);
    throw error;
  }
};

const DownloadButtons: React.FC<DownloadButtonsProps> = ({
  imageUrl,
  markdownUrl,
  chatId,
  disabled = false,
}) => {
  const [downloadingPng, setDownloadingPng] = useState(false);
  const [downloadingMd, setDownloadingMd] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePngDownload = async () => {
    if (!imageUrl || downloadingPng || disabled) return;
    
    setDownloadingPng(true);
    setError(null);
    
    try {
      await downloadFile(imageUrl, `diagram-${chatId}.png`);
    } catch (err) {
      setError('Failed to download PNG');
      console.error('PNG download error:', err);
    } finally {
      setDownloadingPng(false);
    }
  };

  const handleMarkdownDownload = async () => {
    if (!markdownUrl || downloadingMd || disabled) return;
    
    setDownloadingMd(true);
    setError(null);
    
    try {
      await downloadFile(markdownUrl, `diagram-${chatId}.md`);
    } catch (err) {
      setError('Failed to download Markdown');
      console.error('Markdown download error:', err);
    } finally {
      setDownloadingMd(false);
    }
  };

  // Don't render if no URLs are available
  if (!imageUrl && !markdownUrl) {
    return null;
  }

  return (
    <div className="flex flex-col space-y-2">
      <div className="flex items-center space-x-2">
        {/* PNG Download Button */}
        {imageUrl && (
          <button
            onClick={handlePngDownload}
            disabled={disabled || downloadingPng}
            className={`
              inline-flex items-center px-3 py-1.5
              text-sm font-medium rounded-md
              transition-colors duration-200
              ${disabled || downloadingPng
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-green-100 text-green-700 hover:bg-green-200 active:bg-green-300'
              }
            `}
            aria-label="Download PNG image"
            data-testid="download-png-button"
          >
            {downloadingPng ? (
              <>
                <svg 
                  className="animate-spin h-4 w-4 mr-1.5" 
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
                <span>Downloading...</span>
              </>
            ) : (
              <>
                <svg 
                  className="h-4 w-4 mr-1.5" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" 
                  />
                </svg>
                <span>PNG</span>
              </>
            )}
          </button>
        )}

        {/* Markdown Download Button */}
        {markdownUrl && (
          <button
            onClick={handleMarkdownDownload}
            disabled={disabled || downloadingMd}
            className={`
              inline-flex items-center px-3 py-1.5
              text-sm font-medium rounded-md
              transition-colors duration-200
              ${disabled || downloadingMd
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-blue-100 text-blue-700 hover:bg-blue-200 active:bg-blue-300'
              }
            `}
            aria-label="Download Markdown file"
            data-testid="download-markdown-button"
          >
            {downloadingMd ? (
              <>
                <svg 
                  className="animate-spin h-4 w-4 mr-1.5" 
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
                <span>Downloading...</span>
              </>
            ) : (
              <>
                <svg 
                  className="h-4 w-4 mr-1.5" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
                  />
                </svg>
                <span>Markdown</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <p className="text-xs text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  );
};

export default DownloadButtons;
