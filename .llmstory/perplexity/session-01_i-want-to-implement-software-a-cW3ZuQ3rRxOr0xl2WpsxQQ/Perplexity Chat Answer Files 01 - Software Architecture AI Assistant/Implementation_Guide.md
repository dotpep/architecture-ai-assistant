# Software Architecture AI Assistant - Implementation Guide

## QUICK START DEVELOPMENT GUIDE

### Prerequisites
- Node.js 18+ or Python 3.10+
- Docker & Docker Compose
- Git
- OpenAI API key (or alternative LLM)
- PostgreSQL 14+
- Redis 7+

---

## 1. PROJECT SETUP

### Backend Initialization (NestJS Recommended)

```bash
# Create project
nest new architecture-ai-backend
cd architecture-ai-backend

# Install dependencies
npm install @nestjs/core @nestjs/common @nestjs/config
npm install langchain openai anthropic
npm install dagre cytoscape-dagre
npm install postgres pg
npm install redis
npm install prisma @prisma/client
npm install socket.io @nestjs/websockets
npm install multer @types/multer
npm install class-validator class-transformer
npm install @nestjs/jwt @nestjs/passport
npm install passport passport-jwt
```

### Frontend Initialization (Next.js Recommended)

```bash
# Create Next.js project
npx create-next-app@latest architecture-ai-frontend --typescript
cd architecture-ai-frontend

# Install dependencies
npm install react-flow-renderer
npm install zustand
npm install socket.io-client
npm install axios
npm install next-auth
npm install react-markdown
npm install html2canvas jspdf
npm install framer-motion
npm install react-hot-toast
npm install recharts
npm install @headlessui/react
```

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: arch_ai
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: architecture_ai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps
```

---

## 2. DATABASE SCHEMA (Prisma)

```prisma
// prisma/schema.prisma

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id                String      @id @default(cuid())
  email             String      @unique
  passwordHash      String?
  name              String?
  createdAt         DateTime    @default(now())
  updatedAt         DateTime    @updatedAt
  subscription      String      @default("free") // free, pro, enterprise
  apiQuota          Int         @default(100)
  diagrams          Diagram[]
  projects          Project[]
  collaborations    Collaboration[]
  comments          Comment[]
}

model Project {
  id          String      @id @default(cuid())
  userId      String
  user        User        @relation(fields: [userId], references: [id], onDelete: Cascade)
  name        String
  description String?
  diagrams    Diagram[]
  members     Collaboration[]
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt
}

model Diagram {
  id              String        @id @default(cuid())
  userId          String
  user            User          @relation(fields: [userId], references: [id], onDelete: Cascade)
  projectId       String?
  project         Project?      @relation(fields: [projectId], references: [id], onDelete: SetNull)
  title           String
  description     String?
  nodes           DiagramNode[]
  edges           DiagramEdge[]
  versions        DiagramVersion[]
  comments        Comment[]
  metadata        Json?
  pattern         String? // microservices, layered, event-driven, etc.
  technologies    String[] // nodejs, python, go, etc.
  estimatedCost   Float?
  scalingRating   Int? // 1-5
  visibility      String        @default("private") // private, shared, public
  createdAt       DateTime      @default(now())
  updatedAt       DateTime      @updatedAt
  generatedAt     DateTime?
  lastExportedAt  DateTime?
}

model DiagramNode {
  id          String      @id @default(cuid())
  diagramId   String
  diagram     Diagram     @relation(fields: [diagramId], references: [id], onDelete: Cascade)
  type        String      // service, database, queue, cache, etc.
  label       String
  icon        String?     // URL to icon
  description String?
  position    Json        // { x: number, y: number }
  properties  Json?
  style       Json?
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt
  outgoing    DiagramEdge[] @relation("source")
  incoming    DiagramEdge[] @relation("target")
}

model DiagramEdge {
  id          String      @id @default(cuid())
  diagramId   String
  diagram     Diagram     @relation(fields: [diagramId], references: [id], onDelete: Cascade)
  sourceId    String
  source      DiagramNode @relation("source", fields: [sourceId], references: [id], onDelete: Cascade)
  targetId    String
  target      DiagramNode @relation("target", fields: [targetId], references: [id], onDelete: Cascade)
  type        String      // sync, async, rpc, grpc, etc.
  label       String?
  protocol    String?
  properties  Json?
  style       Json?
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt
}

model DiagramVersion {
  id        String    @id @default(cuid())
  diagramId String
  diagram   Diagram   @relation(fields: [diagramId], references: [id], onDelete: Cascade)
  version   Int
  snapshot  Json      // Full diagram state
  message   String?
  createdAt DateTime  @default(now())
  createdBy String
}

model Collaboration {
  id        String    @id @default(cuid())
  userId    String
  user      User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  projectId String
  project   Project   @relation(fields: [projectId], references: [id], onDelete: Cascade)
  role      String    @default("viewer") // viewer, editor, admin
  createdAt DateTime  @default(now())

  @@unique([userId, projectId])
}

model Comment {
  id        String    @id @default(cuid())
  userId    String
  user      User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  diagramId String
  diagram   Diagram   @relation(fields: [diagramId], references: [id], onDelete: Cascade)
  nodeId    String?
  content   String
  resolved  Boolean   @default(false)
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt
}

model GenerationLog {
  id              String    @id @default(cuid())
  userId          String
  prompt          String
  llmModel        String
  generationTime  Int       // milliseconds
  tokensUsed      Int
  costEstimate    Float
  success         Boolean
  errorMessage    String?
  createdAt       DateTime  @default(now())
}
```

---

## 3. CORE SERVICE MODULES

### AI Generation Service

```typescript
// src/services/ai-generation.service.ts

import { Injectable } from '@nestjs/common';
import { OpenAI } from 'langchain/llms/openai';
import { PromptTemplate } from 'langchain/prompts';

@Injectable()
export class AiGenerationService {
  private llm: OpenAI;

  constructor() {
    this.llm = new OpenAI({
      openAIApiKey: process.env.OPENAI_API_KEY,
      modelName: 'gpt-4',
      temperature: 0.7,
    });
  }

  async generateArchitecture(
    userInput: string,
    pattern?: string,
    technologies?: string[]
  ): Promise<ArchitectureResponse> {
    const prompt = this.buildPrompt(userInput, pattern, technologies);
    
    try {
      const response = await this.llm.call(prompt);
      const parsed = this.parseResponse(response);
      return {
        nodes: parsed.nodes,
        edges: parsed.edges,
        metadata: parsed.metadata,
        generationTime: Date.now(),
      };
    } catch (error) {
      throw new Error(`AI generation failed: ${error.message}`);
    }
  }

  private buildPrompt(
    userInput: string,
    pattern?: string,
    technologies?: string[]
  ): string {
    const patternHint = pattern
      ? `Use a ${pattern} architecture pattern.`
      : 'Choose the best architecture pattern.';

    const techHint = technologies?.length
      ? `Preferred technologies: ${technologies.join(', ')}`
      : '';

    return `
You are an expert software architect. Generate a system architecture diagram.

User Requirements: ${userInput}

${patternHint}
${techHint}

Generate a JSON response with this structure:
{
  "nodes": [
    {
      "id": "string",
      "type": "service|database|queue|cache|api_gateway",
      "label": "string",
      "description": "string",
      "properties": {}
    }
  ],
  "edges": [
    {
      "source": "node_id",
      "target": "node_id",
      "type": "sync|async|grpc|websocket",
      "protocol": "http|grpc|amqp|kafka"
    }
  ],
  "metadata": {
    "pattern": "string",
    "rationale": "string",
    "technologies": ["string"],
    "scalabilityScore": 1-5,
    "complexityLevel": "simple|moderate|complex"
  }
}

Only return valid JSON, no other text.
    `;
  }

  private parseResponse(response: string): ParsedArchitecture {
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) throw new Error('No JSON found in response');
      return JSON.parse(jsonMatch[0]);
    } catch (error) {
      throw new Error(`Failed to parse AI response: ${error.message}`);
    }
  }
}
```

### Diagram Processing Service

```typescript
// src/services/diagram-processing.service.ts

import { Injectable } from '@nestjs/common';
import * as dagre from 'dagre';

@Injectable()
export class DiagramProcessingService {
  computeLayout(nodes: DiagramNode[], edges: DiagramEdge[]): LayoutResult {
    const g = new dagre.graphlib.Graph();
    g.setGraph({ rankdir: 'TB', nodesep: 50, ranksep: 50 });
    g.setDefaultEdgeLabel(() => ({}));

    // Add nodes
    nodes.forEach(node => {
      g.setNode(node.id, {
        label: node.label,
        width: 120,
        height: 80,
      });
    });

    // Add edges
    edges.forEach(edge => {
      g.setEdge(edge.sourceId, edge.targetId);
    });

    // Compute layout
    dagre.layout(g);

    // Extract positions
    const positions = {};
    g.nodes().forEach(nodeId => {
      const node = g.node(nodeId);
      positions[nodeId] = {
        x: node.x,
        y: node.y,
      };
    });

    return { positions, width: g.graph().width, height: g.graph().height };
  }

  validateDiagram(diagram: Diagram): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Check for cycles (if applicable)
    if (this.hasCycle(diagram.nodes, diagram.edges)) {
      warnings.push('Diagram contains circular dependencies');
    }

    // Check for isolated nodes
    diagram.nodes.forEach(node => {
      const hasConnection = diagram.edges.some(
        e => e.sourceId === node.id || e.targetId === node.id
      );
      if (!hasConnection) {
        warnings.push(`Node "${node.label}" is isolated`);
      }
    });

    // Check for orphaned edges
    diagram.edges.forEach(edge => {
      const sourceExists = diagram.nodes.some(n => n.id === edge.sourceId);
      const targetExists = diagram.nodes.some(n => n.id === edge.targetId);
      if (!sourceExists || !targetExists) {
        errors.push(`Edge references non-existent nodes`);
      }
    });

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }

  private hasCycle(
    nodes: DiagramNode[],
    edges: DiagramEdge[]
  ): boolean {
    const graph = new Map<string, string[]>();
    
    nodes.forEach(node => {
      graph.set(node.id, []);
    });

    edges.forEach(edge => {
      graph.get(edge.sourceId)?.push(edge.targetId);
    });

    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    const isCyclic = (nodeId: string): boolean => {
      visited.add(nodeId);
      recursionStack.add(nodeId);

      for (const neighbor of graph.get(nodeId) || []) {
        if (!visited.has(neighbor)) {
          if (isCyclic(neighbor)) return true;
        } else if (recursionStack.has(neighbor)) {
          return true;
        }
      }

      recursionStack.delete(nodeId);
      return false;
    };

    for (const nodeId of nodes.map(n => n.id)) {
      if (!visited.has(nodeId)) {
        if (isCyclic(nodeId)) return true;
      }
    }

    return false;
  }
}
```

### Code Analysis Service

```typescript
// src/services/code-analysis.service.ts

import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class CodeAnalysisService {
  async analyzeRepository(repoPath: string): Promise<ArchitectureAnalysis> {
    const packageJson = await this.readPackageJson(repoPath);
    const structure = await this.analyzeFileStructure(repoPath);
    const dependencies = this.extractDependencies(packageJson);
    const pattern = this.detectPattern(structure, dependencies);

    return {
      technologies: this.detectTechnologies(packageJson),
      dependencies,
      structure,
      detectedPattern: pattern,
      components: this.extractComponents(structure),
      recommendations: this.generateRecommendations(pattern, dependencies),
    };
  }

  private async readPackageJson(repoPath: string): Promise<any> {
    const pkgPath = path.join(repoPath, 'package.json');
    if (fs.existsSync(pkgPath)) {
      return JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
    }
    return {};
  }

  private detectTechnologies(packageJson: any): string[] {
    const techs: string[] = [];

    if (packageJson.dependencies) {
      const deps = Object.keys(packageJson.dependencies);

      if (deps.some(d => d.includes('react'))) techs.push('React');
      if (deps.some(d => d.includes('express'))) techs.push('Express');
      if (deps.some(d => d.includes('fastapi'))) techs.push('FastAPI');
      if (deps.some(d => d.includes('postgres'))) techs.push('PostgreSQL');
      if (deps.some(d => d.includes('mongodb'))) techs.push('MongoDB');
      if (deps.some(d => d.includes('redis'))) techs.push('Redis');
    }

    return techs;
  }

  private extractDependencies(packageJson: any): Dependency[] {
    return Object.entries(packageJson.dependencies || {}).map(
      ([name, version]) => ({
        name,
        version: version as string,
        type: 'prod',
      })
    );
  }

  private detectPattern(
    structure: FileStructure,
    dependencies: Dependency[]
  ): string {
    // Simple heuristic-based pattern detection
    const hasServices = structure.directories.some(d =>
      d.includes('service') || d.includes('services')
    );
    const hasControllers = structure.directories.some(d =>
      d.includes('controller') || d.includes('controllers')
    );
    const hasLayers = ['services', 'controllers', 'models'].every(layer =>
      structure.directories.some(d => d.includes(layer))
    );

    if (hasServices && !hasControllers && !hasLayers) {
      return 'microservices';
    } else if (hasLayers) {
      return 'layered';
    } else if (dependencies.some(d => d.name.includes('kafka'))) {
      return 'event-driven';
    }

    return 'modular';
  }

  private generateRecommendations(
    pattern: string,
    dependencies: Dependency[]
  ): string[] {
    const recommendations: string[] = [];

    if (pattern === 'microservices' && !dependencies.some(d => d.name.includes('docker'))) {
      recommendations.push('Consider containerizing services with Docker');
    }

    if (pattern === 'microservices' && !dependencies.some(d => d.name.includes('kubernetes'))) {
      recommendations.push('Consider orchestrating with Kubernetes');
    }

    return recommendations;
  }

  // ... additional helper methods
}
```

---

## 4. API ENDPOINTS (NestJS Controllers)

```typescript
// src/controllers/diagram.controller.ts

import { Controller, Post, Get, Body, Param, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

@Controller('api/v1/diagrams')
@UseGuards(JwtAuthGuard)
export class DiagramController {
  constructor(
    private diagramService: DiagramService,
    private aiService: AiGenerationService,
    private processingService: DiagramProcessingService
  ) {}

  @Post('generate')
  async generate(@Body() dto: GenerateDiagramDto) {
    const architecture = await this.aiService.generateArchitecture(
      dto.prompt,
      dto.pattern,
      dto.technologies
    );

    const layout = this.processingService.computeLayout(
      architecture.nodes,
      architecture.edges
    );

    return this.diagramService.createDiagram({
      ...architecture,
      layout,
    });
  }

  @Get(':id')
  async getDiagram(@Param('id') id: string) {
    return this.diagramService.getDiagram(id);
  }

  @Post(':id/export')
  async exportDiagram(
    @Param('id') id: string,
    @Body() dto: ExportDiagramDto
  ) {
    const diagram = await this.diagramService.getDiagram(id);
    return this.diagramService.export(diagram, dto.format);
  }

  @Post(':id/generate-docs')
  async generateDocumentation(
    @Param('id') id: string,
    @Body() dto: GenerateDocsDto
  ) {
    const diagram = await this.diagramService.getDiagram(id);
    return this.diagramService.generateDocumentation(diagram, dto.format);
  }
}
```

---

## 5. FRONTEND COMPONENTS (React/Next.js)

```typescript
// components/DiagramCanvas.tsx

import React, { useCallback, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
} from 'react-flow-renderer';

interface DiagramCanvasProps {
  initialNodes: Node[];
  initialEdges: Edge[];
  onSave: (nodes: Node[], edges: Edge[]) => void;
}

export const DiagramCanvas: React.FC<DiagramCanvasProps> = ({
  initialNodes,
  initialEdges,
  onSave,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const handleSave = useCallback(() => {
    onSave(nodes, edges);
  }, [nodes, edges, onSave]);

  return (
    <div style={{ width: '100%', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
      <button onClick={handleSave}>Save Diagram</button>
    </div>
  );
};
```

---

## 6. DEPLOYMENT

### Docker Build

```dockerfile
# Dockerfile.backend
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY dist ./dist

EXPOSE 3000

CMD ["node", "dist/main.js"]
```

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --only=production

EXPOSE 3000
CMD ["npm", "run", "start"]
```

### Kubernetes Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: architecture-ai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: architecture-ai-backend
  template:
    metadata:
      labels:
        app: architecture-ai-backend
    spec:
      containers:
      - name: backend
        image: architecture-ai-backend:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## 7. TESTING STRATEGY

```typescript
// src/services/__tests__/ai-generation.service.spec.ts

import { Test } from '@nestjs/testing';
import { AiGenerationService } from '../ai-generation.service';

describe('AiGenerationService', () => {
  let service: AiGenerationService;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [AiGenerationService],
    }).compile();

    service = module.get<AiGenerationService>(AiGenerationService);
  });

  it('should generate architecture from text prompt', async () => {
    const result = await service.generateArchitecture(
      'Build a microservices architecture for an e-commerce platform'
    );

    expect(result.nodes).toBeDefined();
    expect(result.edges).toBeDefined();
    expect(result.metadata).toBeDefined();
  });

  it('should parse AI response correctly', async () => {
    const invalidJson = 'This is not JSON';
    expect(() => service.parseResponse(invalidJson)).toThrow();
  });
});
```

---

## 8. ENVIRONMENT CONFIGURATION

```bash
# .env.example

# Database
DATABASE_URL=postgresql://arch_ai:secure_password@localhost:5432/architecture_ai

# Redis
REDIS_URL=redis://localhost:6379

# AI/LLM
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4

# AWS S3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=architecture-ai-diagrams
AWS_REGION=us-east-1

# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=7d

# Application
NODE_ENV=production
PORT=3000
FRONTEND_URL=https://app.architecture-ai.com

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

---

## 9. KEY PERFORMANCE OPTIMIZATION

```typescript
// src/common/caching.middleware.ts

import { Injectable, NestMiddleware } from '@nestjs/common';
import { RedisService } from '../redis/redis.service';

@Injectable()
export class CachingMiddleware implements NestMiddleware {
  constructor(private redis: RedisService) {}

  async use(req: any, res: any, next: Function) {
    const cacheKey = `${req.method}:${req.url}`;

    // Check cache for GET requests
    if (req.method === 'GET') {
      const cached = await this.redis.get(cacheKey);
      if (cached) {
        return res.json(JSON.parse(cached));
      }
    }

    // Intercept response to cache it
    const originalJson = res.json;
    res.json = (data: any) => {
      if (req.method === 'GET') {
        this.redis.set(cacheKey, JSON.stringify(data), 3600); // 1 hour TTL
      }
      return originalJson.call(res, data);
    };

    next();
  }
}
```

---

## 10. MONITORING & LOGGING

```typescript
// src/common/logging.middleware.ts

import { Injectable, Logger, NestMiddleware } from '@nestjs/common';

@Injectable()
export class LoggingMiddleware implements NestMiddleware {
  private logger = new Logger('HTTP');

  use(req: any, res: any, next: Function) {
    const { method, originalUrl } = req;
    const start = Date.now();

    res.on('finish', () => {
      const duration = Date.now() - start;
      const { statusCode } = res;

      this.logger.log(
        `${method} ${originalUrl} ${statusCode} - ${duration}ms`
      );
    });

    next();
  }
}
```

---

## NEXT STEPS

1. **Clone the repository** and follow setup instructions
2. **Create .env** from .env.example
3. **Run migrations**: `npx prisma migrate dev`
4. **Start development servers**: `docker-compose up && npm run dev`
5. **Run tests**: `npm run test`
6. **Deploy to staging**: Follow CI/CD pipeline

---

**Version**: 1.0
**Last Updated**: December 2025
