# Architecture AI Assistant - Frontend

React + TypeScript + Vite frontend application for the Architecture AI Assistant.

## Setup Complete ✓

This project has been initialized with:

- **React 19** with TypeScript
- **Vite** as the build tool
- **Tailwind CSS** for styling
- **Axios** for API calls
- **React Flow** for diagram rendering

## Project Structure

```
src/
├── types/
│   └── index.ts          # TypeScript type definitions
├── services/
│   └── api.ts            # API service module
├── vite-env.d.ts         # Vite environment types
├── App.jsx               # Main application component (to be converted to TSX)
├── main.jsx              # Entry point (to be converted to TSX)
└── index.css             # Global styles with Tailwind
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
VITE_API_BASE_URL=https://your-api-gateway-url.execute-api.region.amazonaws.com/dev
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production (includes TypeScript compilation)
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Type Definitions

All TypeScript types are defined in `src/types/index.ts`:

- `DiagramType` - Supported diagram types
- `ChatMessage` - Chat message structure
- `GenerateDiagramRequest/Response` - API request/response types
- `SaveChatRequest/Response` - Chat save API types
- `ChatHistoryResponse` - Chat history API types

## API Service

The `src/services/api.ts` module provides three main functions:

- `generateDiagram(request)` - Generate diagram from user prompt
- `getChatHistory(params)` - Get paginated chat history
- `saveChat(request)` - Save chat message to DynamoDB

All API calls use Axios with proper error handling and TypeScript types.

## Next Steps

The following tasks are ready to be implemented:

1. Convert existing JSX files to TSX
2. Implement frontend components (Header, ChatInput, DiagramRenderer, etc.)
3. Integrate API service with components
4. Add React Flow diagram rendering
5. Implement chat history loading

## Requirements Satisfied

- ✓ **Requirement 8.1**: React application with TypeScript and Vite
- ✓ **Requirement 1.1, 2.4**: TypeScript type definitions for all data structures
- ✓ **Requirement 7.1, 7.2, 7.3**: API service module with all three endpoints
