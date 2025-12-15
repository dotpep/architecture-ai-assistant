/**
 * DiagramPreview Component
 * Wrapper for DiagramRenderer with toggle between React Flow and S3 PNG preview
 */

import React, { useState } from 'react';
import DiagramRenderer from './DiagramRenderer';

interface DiagramPreviewProps {
  mermaidCode: string;
  imageUrl?: string;
  height?: string | number;
}

const DiagramPreview: React.FC<DiagramPreviewProps> = ({
  mermaidCode,
  imageUrl,
  height = 400,
}) => {
  const [viewMode, setViewMode] = useState<'reactflow' | 'mermaid'>('reactflow');
  const [imageError, setImageError] = useState(false);

  const toggleView = () => {
    setViewMode((prev) => (prev === 'reactflow' ? 'mermaid' : 'reactflow'));
    setImageError(false);
  };

  // Only show toggle button if imageUrl is available
  const canShowMermaidPreview = !!imageUrl;

  return (
    <div className="relative">
      {/* Toggle Button - only show if S3 image is available */}
      {canShowMermaidPreview && (
        <div className="absolute top-2 right-2 z-10">
          <button
            onClick={toggleView}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-700 border border-indigo-700 rounded-lg transition-all shadow-md hover:shadow-lg"
            title={viewMode === 'reactflow' ? 'Switch to PNG Preview' : 'Switch to React Flow Preview'}
          >
            {viewMode === 'reactflow' ? (
              <>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                PNG Preview
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
                React Flow
              </>
            )}
          </button>
        </div>
      )}

      {/* Content */}
      {viewMode === 'reactflow' ? (
        <DiagramRenderer mermaidCode={mermaidCode} height={height} />
      ) : (
        <div
          className="flex items-center justify-center bg-slate-100 rounded-lg border border-slate-300 overflow-auto"
          style={{ height }}
        >
          {imageError ? (
            <div className="text-center p-4">
              <svg className="w-12 h-12 text-slate-400 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-slate-600 text-sm">Failed to load image</p>
            </div>
          ) : imageUrl ? (
            <img
              src={imageUrl}
              alt="Diagram PNG"
              className="max-w-full max-h-full object-contain p-4"
              onError={() => setImageError(true)}
            />
          ) : null}
        </div>
      )}
    </div>
  );
};

export default DiagramPreview;
