/**
 * DiagramRenderer Component
 * Renders Mermaid diagrams using React Flow with zoom and pan controls
 * Requirements: 2.3, 9.2, 9.3, 9.4
 */

import React, { useCallback, useMemo, useEffect, useState } from 'react';
import ReactFlow, {
  Node,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { parseMermaidCode, applyAutoLayout } from '../utils/mermaidParser';

interface DiagramRendererProps {
  mermaidCode: string;
  height?: string | number;
  showMiniMap?: boolean;
  showControls?: boolean;
}

/**
 * DiagramRenderer Component
 * Parses Mermaid code and renders it as an interactive React Flow diagram
 */
const DiagramRenderer: React.FC<DiagramRendererProps> = ({
  mermaidCode,
  height = 400,
  showMiniMap = true,
  showControls = true,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [diagramType, setDiagramType] = useState<string>('unknown');
  const [parseError, setParseError] = useState<string | null>(null);

  // Parse Mermaid code when it changes
  useEffect(() => {
    if (!mermaidCode) {
      setNodes([]);
      setEdges([]);
      setDiagramType('unknown');
      setParseError(null);
      return;
    }

    try {
      const parsed = parseMermaidCode(mermaidCode);
      
      if (parsed.nodes.length === 0) {
        setParseError('No diagram elements found in the code');
        setNodes([]);
        setEdges([]);
        return;
      }

      // Apply automatic layout to prevent node overlap
      const layoutedNodes = applyAutoLayout(parsed.nodes, parsed.edges);
      
      setNodes(layoutedNodes);
      setEdges(parsed.edges);
      setDiagramType(parsed.diagramType);
      setParseError(null);
    } catch (error) {
      console.error('Failed to parse Mermaid code:', error);
      setParseError('Failed to parse diagram code');
      setNodes([]);
      setEdges([]);
    }
  }, [mermaidCode, setNodes, setEdges]);

  // Fit view when nodes change
  const onInit = useCallback((reactFlowInstance: { fitView: () => void }) => {
    setTimeout(() => {
      reactFlowInstance.fitView();
    }, 100);
  }, []);

  // Get diagram type label for display
  const diagramTypeLabel = useMemo(() => {
    const labels: Record<string, string> = {
      flowchart: 'Flowchart',
      sequence: 'Sequence Diagram',
      erdiagram: 'ER Diagram',
      class: 'Class Diagram',
      state: 'State Diagram',
      unknown: 'Diagram',
    };
    return labels[diagramType] || 'Diagram';
  }, [diagramType]);

  // MiniMap node color based on diagram type
  const nodeColor = useCallback((_node: Node) => {
    const colors: Record<string, string> = {
      flowchart: '#6366f1',
      sequence: '#10b981',
      erdiagram: '#f59e0b',
      class: '#8b5cf6',
      state: '#ec4899',
    };
    return colors[diagramType] || '#6366f1';
  }, [diagramType]);

  // Render error state
  if (parseError) {
    return (
      <div 
        className="flex items-center justify-center bg-gray-50 rounded-lg border border-gray-200"
        style={{ height }}
        data-testid="diagram-renderer-error"
      >
        <div className="text-center p-4">
          <svg className="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-gray-500 text-sm">{parseError}</p>
        </div>
      </div>
    );
  }

  // Render empty state
  if (nodes.length === 0) {
    return (
      <div 
        className="flex items-center justify-center bg-gray-50 rounded-lg border border-gray-200"
        style={{ height }}
        data-testid="diagram-renderer-empty"
      >
        <div className="text-center p-4">
          <svg className="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
          </svg>
          <p className="text-gray-500 text-sm">No diagram to display</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="bg-white rounded-lg border border-gray-200 overflow-hidden"
      style={{ height }}
      data-testid="diagram-renderer"
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onInit={onInit}
        fitView
        attributionPosition="bottom-left"
        minZoom={0.1}
        maxZoom={2}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
      >
        {/* Background grid */}
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#e5e7eb" />
        
        {/* Zoom and pan controls */}
        {showControls && (
          <Controls 
            showInteractive={false}
            position="bottom-right"
          />
        )}
        
        {/* Mini map for navigation */}
        {showMiniMap && (
          <MiniMap 
            nodeColor={nodeColor}
            maskColor="rgba(0, 0, 0, 0.1)"
            position="top-right"
            pannable
            zoomable
          />
        )}
        
        {/* Diagram type label */}
        <Panel position="top-left" className="bg-white/80 px-2 py-1 rounded text-xs text-gray-600 shadow-sm">
          {diagramTypeLabel}
        </Panel>
      </ReactFlow>
    </div>
  );
};

export default DiagramRenderer;
