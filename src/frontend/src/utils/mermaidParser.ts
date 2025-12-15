/**
 * Mermaid Parser Utility
 * Parses Mermaid code into React Flow nodes and edges
 * Requirements: 9.1
 */

import { Node, Edge, MarkerType } from 'reactflow';

/**
 * Parsed result from Mermaid code
 */
export interface ParsedDiagram {
  nodes: Node[];
  edges: Edge[];
  diagramType: string;
}

/**
 * Node position configuration
 */
const NODE_WIDTH = 150;
const HORIZONTAL_SPACING = 200;
const VERTICAL_SPACING = 100;

/**
 * Detect the diagram type from Mermaid code
 */
export function detectDiagramType(code: string): string {
  const trimmed = code.trim().toLowerCase();
  
  if (trimmed.startsWith('graph') || trimmed.startsWith('flowchart')) {
    return 'flowchart';
  }
  if (trimmed.startsWith('sequencediagram')) {
    return 'sequence';
  }
  if (trimmed.startsWith('erdiagram')) {
    return 'erdiagram';
  }
  if (trimmed.startsWith('classdiagram')) {
    return 'class';
  }
  if (trimmed.startsWith('statediagram')) {
    return 'state';
  }
  
  return 'unknown';
}

/**
 * Parse flowchart/graph Mermaid code
 */
function parseFlowchart(code: string): ParsedDiagram {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  const nodeMap = new Map<string, { label: string; row: number; col: number }>();
  
  const lines = code.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('%%'));
  
  // Skip the first line (graph TD, flowchart LR, etc.)
  const contentLines = lines.slice(1);
  
  let currentRow = 0;
  let currentCol = 0;
  const processedNodes = new Set<string>();
  
  for (const line of contentLines) {
    // Match node definitions and connections
    // Patterns: A[Label], A-->B, A-->|text|B, A--text-->B
    const connectionMatch = line.match(/^(\w+)(?:\[([^\]]*)\])?(?:\s*)(-->|---|-\.->|==>|---)(?:\|([^|]*)\|)?(?:\s*)(\w+)(?:\[([^\]]*)\])?/);
    
    if (connectionMatch) {
      const [, sourceId, sourceLabel, , edgeLabel, targetId, targetLabel] = connectionMatch;
      
      // Add source node if not exists
      if (!nodeMap.has(sourceId)) {
        nodeMap.set(sourceId, {
          label: sourceLabel || sourceId,
          row: currentRow,
          col: currentCol++,
        });
      }
      
      // Add target node if not exists
      if (!nodeMap.has(targetId)) {
        if (currentCol > 2) {
          currentRow++;
          currentCol = 0;
        }
        nodeMap.set(targetId, {
          label: targetLabel || targetId,
          row: currentRow,
          col: currentCol++,
        });
      }
      
      // Add edge
      edges.push({
        id: `e-${sourceId}-${targetId}-${edges.length}`,
        source: sourceId,
        target: targetId,
        label: edgeLabel || undefined,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { strokeWidth: 2 },
      });
      
      processedNodes.add(sourceId);
      processedNodes.add(targetId);
    } else {
      // Check for standalone node definition: A[Label]
      const nodeMatch = line.match(/^(\w+)\[([^\]]*)\]/);
      if (nodeMatch && !processedNodes.has(nodeMatch[1])) {
        const [, nodeId, label] = nodeMatch;
        if (!nodeMap.has(nodeId)) {
          nodeMap.set(nodeId, {
            label: label || nodeId,
            row: currentRow,
            col: currentCol++,
          });
          processedNodes.add(nodeId);
        }
      }
    }
  }
  
  // Convert nodeMap to React Flow nodes with positions
  nodeMap.forEach((data, id) => {
    nodes.push({
      id,
      data: { label: data.label },
      position: {
        x: data.col * HORIZONTAL_SPACING,
        y: data.row * VERTICAL_SPACING,
      },
      style: {
        width: NODE_WIDTH,
        padding: 10,
        borderRadius: 8,
        border: '2px solid #6366f1',
        backgroundColor: '#f0f0ff',
      },
    });
  });
  
  return { nodes, edges, diagramType: 'flowchart' };
}

/**
 * Parse sequence diagram Mermaid code
 */
function parseSequenceDiagram(code: string): ParsedDiagram {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  const participants: string[] = [];
  
  const lines = code.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('%%'));
  
  let messageIndex = 0;
  
  for (const line of lines) {
    // Skip diagram declaration
    if (line.toLowerCase().startsWith('sequencediagram')) continue;
    
    // Match participant declarations
    const participantMatch = line.match(/^participant\s+(\w+)(?:\s+as\s+(.+))?/i);
    if (participantMatch) {
      const [, id] = participantMatch;
      if (!participants.includes(id)) {
        participants.push(id);
      }
      continue;
    }
    
    // Match actor declarations
    const actorMatch = line.match(/^actor\s+(\w+)(?:\s+as\s+(.+))?/i);
    if (actorMatch) {
      const [, id] = actorMatch;
      if (!participants.includes(id)) {
        participants.push(id);
      }
      continue;
    }
    
    // Match messages: A->>B: message, A-->>B: message, etc.
    const messageMatch = line.match(/^(\w+)\s*(->>|-->>|->|-->|-)>?\s*(\w+)\s*:\s*(.+)/);
    if (messageMatch) {
      const [, source, , target, message] = messageMatch;
      
      // Add participants if not already added
      if (!participants.includes(source)) participants.push(source);
      if (!participants.includes(target)) participants.push(target);
      
      edges.push({
        id: `e-${source}-${target}-${messageIndex}`,
        source,
        target,
        label: message,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { strokeWidth: 2 },
        labelStyle: { fontSize: 10 },
      });
      
      messageIndex++;
    }
  }
  
  // Create nodes for participants
  participants.forEach((participant, index) => {
    nodes.push({
      id: participant,
      data: { label: participant },
      position: {
        x: index * HORIZONTAL_SPACING,
        y: 0,
      },
      style: {
        width: NODE_WIDTH,
        padding: 10,
        borderRadius: 8,
        border: '2px solid #10b981',
        backgroundColor: '#ecfdf5',
      },
    });
  });
  
  return { nodes, edges, diagramType: 'sequence' };
}

/**
 * Parse ER diagram Mermaid code
 */
function parseERDiagram(code: string): ParsedDiagram {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  const entities = new Map<string, { attributes: string[] }>();
  
  const lines = code.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('%%'));
  
  for (const line of lines) {
    // Skip diagram declaration
    if (line.toLowerCase().startsWith('erdiagram')) continue;
    
    // Match relationships: ENTITY1 ||--o{ ENTITY2 : relationship
    const relationMatch = line.match(/^(\w+)\s*(\|\||\|o|o\||o{|\}o|\}\||\|\{|\{o|\{\|)--(\|\||\|o|o\||o{|\}o|\}\||\|\{|\{o|\{\|)\s*(\w+)\s*:\s*(.+)/);
    if (relationMatch) {
      const [, entity1, , , entity2, relationship] = relationMatch;
      
      if (!entities.has(entity1)) {
        entities.set(entity1, { attributes: [] });
      }
      if (!entities.has(entity2)) {
        entities.set(entity2, { attributes: [] });
      }
      
      edges.push({
        id: `e-${entity1}-${entity2}-${edges.length}`,
        source: entity1,
        target: entity2,
        label: relationship,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { strokeWidth: 2 },
      });
      continue;
    }
    
    // Match entity attributes: ENTITY { type attribute }
    const entityMatch = line.match(/^(\w+)\s*\{/);
    if (entityMatch) {
      const entityName = entityMatch[1];
      if (!entities.has(entityName)) {
        entities.set(entityName, { attributes: [] });
      }
    }
  }
  
  // Create nodes for entities
  let row = 0;
  let col = 0;
  entities.forEach((_, entityName) => {
    nodes.push({
      id: entityName,
      data: { label: entityName },
      position: {
        x: col * HORIZONTAL_SPACING,
        y: row * VERTICAL_SPACING,
      },
      style: {
        width: NODE_WIDTH,
        padding: 10,
        borderRadius: 4,
        border: '2px solid #f59e0b',
        backgroundColor: '#fffbeb',
      },
    });
    
    col++;
    if (col > 2) {
      col = 0;
      row++;
    }
  });
  
  return { nodes, edges, diagramType: 'erdiagram' };
}

/**
 * Main parser function - parses Mermaid code into React Flow format
 */
export function parseMermaidCode(code: string): ParsedDiagram {
  if (!code || typeof code !== 'string') {
    return { nodes: [], edges: [], diagramType: 'unknown' };
  }
  
  const diagramType = detectDiagramType(code);
  
  switch (diagramType) {
    case 'flowchart':
      return parseFlowchart(code);
    case 'sequence':
      return parseSequenceDiagram(code);
    case 'erdiagram':
      return parseERDiagram(code);
    default:
      // For unsupported types, try flowchart parsing as fallback
      return parseFlowchart(code);
  }
}

/**
 * Apply automatic layout to nodes to prevent overlap
 * Uses a simple grid-based layout algorithm
 */
export function applyAutoLayout(nodes: Node[], edges: Edge[]): Node[] {
  if (nodes.length === 0) return nodes;
  
  // Build adjacency list
  const adjacency = new Map<string, string[]>();
  nodes.forEach(node => adjacency.set(node.id, []));
  
  edges.forEach(edge => {
    const targets = adjacency.get(edge.source) || [];
    targets.push(edge.target);
    adjacency.set(edge.source, targets);
  });
  
  // Find root nodes (nodes with no incoming edges)
  const hasIncoming = new Set<string>();
  edges.forEach(edge => hasIncoming.add(edge.target));
  
  const roots = nodes.filter(node => !hasIncoming.has(node.id));
  if (roots.length === 0 && nodes.length > 0) {
    roots.push(nodes[0]);
  }
  
  // BFS to assign levels
  const levels = new Map<string, number>();
  const visited = new Set<string>();
  const queue: { id: string; level: number }[] = roots.map(r => ({ id: r.id, level: 0 }));
  
  while (queue.length > 0) {
    const { id, level } = queue.shift()!;
    if (visited.has(id)) continue;
    visited.add(id);
    levels.set(id, level);
    
    const targets = adjacency.get(id) || [];
    targets.forEach(target => {
      if (!visited.has(target)) {
        queue.push({ id: target, level: level + 1 });
      }
    });
  }
  
  // Handle disconnected nodes
  nodes.forEach(node => {
    if (!levels.has(node.id)) {
      levels.set(node.id, 0);
    }
  });
  
  // Group nodes by level
  const levelGroups = new Map<number, string[]>();
  levels.forEach((level, id) => {
    const group = levelGroups.get(level) || [];
    group.push(id);
    levelGroups.set(level, group);
  });
  
  // Assign positions based on levels
  const positionedNodes = nodes.map(node => {
    const level = levels.get(node.id) || 0;
    const group = levelGroups.get(level) || [];
    const indexInGroup = group.indexOf(node.id);
    
    return {
      ...node,
      position: {
        x: indexInGroup * HORIZONTAL_SPACING,
        y: level * VERTICAL_SPACING,
      },
    };
  });
  
  return positionedNodes;
}

export default parseMermaidCode;
