# Build System and Dependencies

> **Relevant source files**
> * [src/frontend/README.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/README.md)
> * [src/frontend/index.html](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/index.html)
> * [src/frontend/package-lock.json](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package-lock.json)
> * [src/frontend/package.json](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json)
> * [src/frontend/src/index.css](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/src/index.css)

This document describes the frontend build system, dependency management, and compilation pipeline for the Architecture AI Assistant. It covers the Vite build tool configuration, npm package ecosystem, TypeScript compilation, and the complete build-to-deployment workflow.

For frontend application structure and component hierarchy, see [Frontend Application](/dotpep/architecture-ai-assistant/3-frontend-application). For deployment processes that utilize the build system, see [Deployment Script](/dotpep/architecture-ai-assistant/6.1-deployment-script).

---

## Build Tool Overview

The frontend uses **Vite** as its build tool and development server. Vite provides fast Hot Module Replacement (HMR) during development and optimized production builds through Rollup bundling.

### Vite Configuration

The build system is centered around Vite 7.2.4, which handles:

* TypeScript transpilation via `esbuild`
* React Fast Refresh for HMR
* Asset optimization and bundling
* Development server with instant updates

**Sources:** [src/frontend/package.json L32](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L32-L32)

 [src/frontend/package-lock.json L30](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package-lock.json#L30-L30)

---

## Package Management and Scripts

The frontend uses npm as its package manager, with all dependencies locked via `package-lock.json` (lockfileVersion 3).

### NPM Scripts

| Script | Command | Purpose |
| --- | --- | --- |
| `dev` | `vite` | Start development server with HMR at [http://localhost:5173](http://localhost:5173) |
| `build` | `tsc && vite build` | Compile TypeScript and build production bundle |
| `lint` | `eslint .` | Run ESLint on all source files |
| `preview` | `vite preview` | Preview production build locally |

The `build` script executes in two phases:

1. **TypeScript Compilation**: `tsc` validates types and emits type declarations
2. **Vite Build**: Creates optimized production bundle in `dist/`

**Sources:** [src/frontend/package.json L6-L10](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L6-L10)

---

## Dependency Architecture

```

```

**Sources:** [src/frontend/package.json L12-L33](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L12-L33)

 [src/frontend/index.html L11](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/index.html#L11-L11)

 [src/frontend/src/index.css L1-L3](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/src/index.css#L1-L3)

---

## Runtime Dependencies

### Core UI Framework

| Package | Version | Purpose |
| --- | --- | --- |
| `react` | 19.2.0 | Core React library with hooks and concurrent features |
| `react-dom` | 19.2.0 | React DOM renderer for browser environments |

React 19 introduces enhanced concurrent rendering and improved server components support. The application uses function components with hooks throughout.

**Sources:** [src/frontend/package.json L16-L17](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L16-L17)

### HTTP Communication

| Package | Version | Purpose |
| --- | --- | --- |
| `axios` | 1.13.2 | Promise-based HTTP client for API communication |

Axios handles all backend API calls to the API Gateway endpoints. It provides request/response interceptors, automatic JSON transformation, and error handling. Used extensively in `src/services/api.ts`.

**Sources:** [src/frontend/package.json L14](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L14-L14)

### Diagram Visualization

| Package | Version | Purpose |
| --- | --- | --- |
| `reactflow` | 11.11.4 | Interactive diagram rendering library |

React Flow powers the interactive diagram visualization in `DiagramRenderer` components. Key sub-packages include:

* `@reactflow/core@11.11.4` - Core rendering engine
* `@reactflow/background@11.3.14` - Grid/dot backgrounds
* `@reactflow/controls@11.2.14` - Zoom/pan controls
* `@reactflow/minimap@11.7.14` - Minimap overview

**Sources:** [src/frontend/package.json L18](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L18-L18)

 [src/frontend/package-lock.json L1068-L1098](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package-lock.json#L1068-L1098)

### Styling System

| Package | Version | Purpose |
| --- | --- | --- |
| `tailwindcss` | 3.4.19 | Utility-first CSS framework |
| `postcss` | 8.5.6 | CSS transformation pipeline |
| `autoprefixer` | 10.4.23 | Adds vendor prefixes automatically |

Tailwind CSS is configured via `@tailwind` directives in `src/index.css`. The PostCSS pipeline processes these directives during build, generating utility classes on-demand.

**Sources:** [src/frontend/package.json L13-L15](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L13-L15)

 [src/frontend/src/index.css L1-L3](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/src/index.css#L1-L3)

---

## Development Dependencies

### TypeScript Toolchain

| Package | Version | Purpose |
| --- | --- | --- |
| `typescript` | 5.9.3 | TypeScript compiler and language service |
| `@types/react` | 19.2.5 | React type definitions |
| `@types/react-dom` | 19.2.3 | React DOM type definitions |
| `@types/node` | 25.0.2 | Node.js type definitions |

TypeScript 5.9 provides strict type checking with decorators support. All source files use `.tsx` extension for JSX + TypeScript. Type definitions ensure compile-time safety for React APIs and Node.js utilities.

**Sources:** [src/frontend/package.json L22-L31](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L22-L31)

### Build Tooling

| Package | Version | Purpose |
| --- | --- | --- |
| `vite` | 7.2.4 | Build tool and dev server |
| `@vitejs/plugin-react` | 5.1.1 | Enables React Fast Refresh |

The Vite plugin for React includes:

* Babel plugins for JSX transformation
* `@babel/plugin-transform-react-jsx-self@7.27.1` - Adds `__self` prop for debugging
* `@babel/plugin-transform-react-jsx-source@7.27.1` - Adds source location metadata

**Sources:** [src/frontend/package.json L25-L32](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L25-L32)

 [src/frontend/package-lock.json L249-L280](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package-lock.json#L249-L280)

### Code Quality

| Package | Version | Purpose |
| --- | --- | --- |
| `eslint` | 9.39.1 | JavaScript/TypeScript linter |
| `@eslint/js` | 9.39.2 | ESLint recommended rules |
| `eslint-plugin-react-hooks` | 7.0.1 | Enforces React hooks rules |
| `eslint-plugin-react-refresh` | 0.4.24 | Validates Fast Refresh compatibility |
| `globals` | 16.5.0 | Global variable definitions for ESLint |

ESLint configuration enforces React best practices, including proper hook usage and Fast Refresh compatibility for all components.

**Sources:** [src/frontend/package.json L21-L29](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L21-L29)

---

## Build Pipeline

### Development Build Flow

```

```

During development (`npm run dev`):

1. Vite starts dev server on port 5173
2. `esbuild` transpiles TypeScript/JSX on-demand
3. PostCSS processes Tailwind directives in CSS files
4. Files served as native ES modules to browser
5. File changes trigger instant HMR updates without full reload

**Sources:** [src/frontend/package.json L7](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L7-L7)

 [src/frontend/index.html L11](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/index.html#L11-L11)

### Production Build Flow

```

```

Production build (`npm run build`) executes:

1. **TypeScript Phase** (`tsc`): * Validates all type annotations * Checks for type errors across entire codebase * Generates `.d.ts` declaration files * Fails build if type errors exist
2. **Vite Build Phase** (`vite build`): * Bundles all modules via Rollup * Tree-shakes unused code * Minifies JavaScript with esbuild * Processes CSS with PostCSS + Tailwind * Optimizes assets (images compressed, fonts subset) * Splits code into chunks for optimal loading * Generates `dist/` directory with: * `index.html` (with hashed asset references) * `assets/*.js` (JavaScript bundles) * `assets/*.css` (processed stylesheets) * Optimized static assets

**Sources:** [src/frontend/package.json L8](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L8-L8)

---

## Environment Configuration

### Build-Time Environment Variables

Environment variables are injected at build time via Vite's environment variable system. All variables prefixed with `VITE_` are exposed to the frontend code.

```

```

**Key Environment Variables:**

| Variable | Purpose | Set By |
| --- | --- | --- |
| `VITE_API_BASE_URL` | API Gateway endpoint URL | `deploy.sh` during build |

The deployment script (`infrastructure/scripts/deploy.sh`) dynamically creates `.env` file with the API Gateway URL from Terraform outputs:

```php
# Phase 3 of deploy.sh injects API URL
API_GATEWAY_URL=$(terraform output -raw api_gateway_url)
echo "VITE_API_BASE_URL=${API_GATEWAY_URL}" > .env
npm run build
```

During build, Vite replaces all `import.meta.env.VITE_API_BASE_URL` references with the actual URL string, creating a fully static bundle with no runtime environment dependency.

**Sources:** [src/frontend/package.json L8](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L8-L8)

 [src/frontend/README.md L33-L35](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/README.md#L33-L35)

---

## Dependency Resolution

### Package Lock Integrity

The `package-lock.json` uses lockfileVersion 3, which provides:

* SHA-512 integrity hashes for all packages
* Exact version pinning across the dependency tree
* Reproducible builds across environments
* Protection against supply chain attacks

All transitive dependencies are locked, including:

* 1,200+ packages in the dependency tree
* Platform-specific esbuild binaries (via optional dependencies)
* React Flow ecosystem packages
* Babel transformation plugins
* ESLint plugin ecosystem

**Sources:** [src/frontend/package-lock.json L4](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package-lock.json#L4-L4)

### Critical Dependency Chains

```

```

**Sources:** [src/frontend/package-lock.json L7-L32](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package-lock.json#L7-L32)

 [src/frontend/package-lock.json L1068-L1132](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package-lock.json#L1068-L1132)

---

## Integration with Deployment

The build system integrates with the broader deployment pipeline:

1. **Local Development**: `npm run dev` serves from `src/` with HMR
2. **Production Build**: `npm run build` creates `dist/` directory
3. **S3 Upload**: `deploy.sh` syncs `dist/` to S3 bucket
4. **CloudFront**: Serves built assets via CDN with caching

For complete deployment workflow, see [Deployment Script](/dotpep/architecture-ai-assistant/6.1-deployment-script). For infrastructure provisioning of S3 and CloudFront, see [CloudFront and S3 Configuration](/dotpep/architecture-ai-assistant/5.3-cloudfront-and-s3-configuration).

**Sources:** [src/frontend/package.json L6-L10](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/package.json#L6-L10)

 [src/frontend/README.md L38-L42](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/README.md#L38-L42)