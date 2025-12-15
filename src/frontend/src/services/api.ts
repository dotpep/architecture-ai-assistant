/**
 * API Service Module
 * Handles all API calls to the backend Lambda functions
 * Requirements: 7.1, 7.2, 7.3
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  GenerateDiagramRequest,
  GenerateDiagramResponse,
  SaveChatRequest,
  SaveChatResponse,
  ChatHistoryResponse,
  ChatHistoryParams,
  Session,
  SessionListResponse,
  CreateSessionResponse,
  UpdateSessionTitleRequest,
  SessionListParams,
  ApiError,
} from '../types';

/**
 * Create axios instance with base configuration
 */
const createApiClient = (): AxiosInstance => {
  const baseURL = import.meta.env.VITE_API_BASE_URL;
  
  if (!baseURL) {
    console.warn('VITE_API_BASE_URL is not set in environment variables');
  }

  return axios.create({
    baseURL,
    timeout: 60000, // 60 seconds for diagram generation
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

const apiClient = createApiClient();

/**
 * Handle API errors and format them consistently
 */
const handleApiError = (error: unknown): never => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;
    
    if (axiosError.response) {
      // Server responded with error status
      const errorMessage = axiosError.response.data?.error || 'An error occurred';
      const errorDetails = axiosError.response.data?.details;
      
      throw new Error(
        errorDetails 
          ? `${errorMessage}: ${errorDetails}` 
          : errorMessage
      );
    } else if (axiosError.request) {
      // Request made but no response received
      throw new Error('No response from server. Please check your connection.');
    }
  }
  
  // Generic error
  throw new Error('An unexpected error occurred');
};

/**
 * Generate a diagram from user prompt
 * POST /api/diagram/generate
 * 
 * @param request - User prompt and diagram type
 * @returns Generated diagram data with S3 URLs
 */
export const generateDiagram = async (
  request: GenerateDiagramRequest
): Promise<GenerateDiagramResponse> => {
  try {
    const response = await apiClient.post<GenerateDiagramResponse>(
      '/api/diagram/generate',
      request
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Get chat history with pagination
 * GET /api/chat/history
 * 
 * @param params - Optional limit and pagination token
 * @returns Array of chat messages
 */
export const getChatHistory = async (
  params?: ChatHistoryParams
): Promise<ChatHistoryResponse> => {
  try {
    const response = await apiClient.get<ChatHistoryResponse>(
      '/api/chat/history',
      { params }
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Save a chat message to DynamoDB
 * POST /api/chat/save
 * 
 * @param request - Chat message data
 * @returns Confirmation with chatId and timestamp
 */
export const saveChat = async (
  request: SaveChatRequest
): Promise<SaveChatResponse> => {
  try {
    const response = await apiClient.post<SaveChatResponse>(
      '/api/chat/save',
      request
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Update API base URL (useful for testing or environment switching)
 */
export const updateApiBaseUrl = (newBaseUrl: string): void => {
  apiClient.defaults.baseURL = newBaseUrl;
};

/**
 * Get current API base URL
 */
export const getApiBaseUrl = (): string | undefined => {
  return apiClient.defaults.baseURL;
};

/**
 * Create a new chat session
 * POST /api/session
 * Requirements: 5.1
 * 
 * @returns New session data
 */
export const createSession = async (): Promise<CreateSessionResponse> => {
  try {
    const response = await apiClient.post<CreateSessionResponse>('/api/session');
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Get list of all sessions with pagination
 * GET /api/session
 * Requirements: 5.2
 * 
 * @param params - Optional limit and pagination token
 * @returns Array of sessions with metadata
 */
export const getSessions = async (
  params?: SessionListParams
): Promise<SessionListResponse> => {
  try {
    const response = await apiClient.get<SessionListResponse>(
      '/api/session',
      { params }
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Get messages for a specific session
 * GET /api/session/{sessionId}/messages
 * Requirements: 5.3
 * 
 * @param sessionId - The session ID to get messages for
 * @returns Array of messages for the session
 */
export const getSessionMessages = async (
  sessionId: string
): Promise<ChatHistoryResponse> => {
  try {
    const response = await apiClient.get<ChatHistoryResponse>(
      `/api/session/${sessionId}/messages`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Update session title
 * PUT /api/session/{sessionId}
 * Requirements: 5.1
 * 
 * @param sessionId - The session ID to update
 * @param request - New title data
 * @returns Updated session data
 */
export const updateSessionTitle = async (
  sessionId: string,
  request: UpdateSessionTitleRequest
): Promise<Session> => {
  try {
    const response = await apiClient.put<Session>(
      `/api/session/${sessionId}`,
      request
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Delete a session
 * DELETE /api/session/{sessionId}
 * Requirements: 5.1
 * 
 * @param sessionId - The session ID to delete
 */
export const deleteSession = async (sessionId: string): Promise<void> => {
  try {
    await apiClient.delete(`/api/session/${sessionId}`);
  } catch (error) {
    return handleApiError(error);
  }
};
