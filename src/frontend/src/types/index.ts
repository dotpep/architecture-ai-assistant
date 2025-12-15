/**
 * Type definitions for Architecture AI Assistant
 * Requirements: 1.1, 2.4
 */

/**
 * Supported diagram types
 */
export type DiagramType = 
  | 'flowchart' 
  | 'erdiagram' 
  | 'sequence' 
  | 'class' 
  | 'state' 
  | 'architecture' 
  | 'dfd';

/**
 * Status of a chat message/diagram generation
 */
export type MessageStatus = 'pending' | 'completed' | 'failed';

/**
 * Chat message structure
 */
export interface ChatMessage {
  chatId: string;
  timestamp: number;
  userMessage: string;
  diagramType: DiagramType;
  aiResponse?: string;
  mermaidCode?: string;
  imageUrl?: string;
  markdownUrl?: string;
  status: MessageStatus;
}

/**
 * Request payload for generating a diagram
 */
export interface GenerateDiagramRequest {
  userPrompt: string;
  diagramType: DiagramType;
}

/**
 * Response from diagram generation API
 */
export interface GenerateDiagramResponse {
  chatId: string;
  timestamp: number;
  mermaidCode: string;
  imageUrl: string;
  markdownUrl: string;
  status: string;
}

/**
 * Request payload for saving a chat message
 */
export interface SaveChatRequest {
  chatId: string;
  userMessage: string;
  diagramType: DiagramType;
}

/**
 * Response from save chat API
 */
export interface SaveChatResponse {
  success: boolean;
  chatId: string;
  timestamp: number;
}

/**
 * Response from chat history API
 */
export interface ChatHistoryResponse {
  chats: ChatMessage[];
  count: number;
  nextToken?: string;
}

/**
 * Query parameters for chat history
 */
export interface ChatHistoryParams {
  limit?: number;
  nextToken?: string;
}

/**
 * API error response
 */
export interface ApiError {
  error: string;
  details?: string;
}
