# CloudFront and S3 Configuration

> **Relevant source files**
> * [infrastructure/terraform/cloudfront.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf)
> * [src/backend/shared/aws_helpers.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/shared/aws_helpers.py)
> * [src/backend/shared/utils.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/shared/utils.py)
> * [src/frontend/src/components/DownloadButtons.tsx](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/src/components/DownloadButtons.tsx)

## Purpose and Scope

This document details the CloudFront distribution and S3 bucket configuration that forms the content delivery layer of the Architecture AI Assistant. CloudFront serves both the React SPA frontend and user-generated diagram files (PNG and markdown) with appropriate caching strategies and security controls.

For the complete infrastructure overview including Lambda, API Gateway, and DynamoDB, see [System Architecture](/dotpep/architecture-ai-assistant/2-system-architecture). For IAM roles and security policies, see [IAM Roles and Security](/dotpep/architecture-ai-assistant/5.4-iam-roles-and-security). For S3 data storage schema, see [Data Storage Architecture](/dotpep/architecture-ai-assistant/2.2-data-storage-architecture).

## CloudFront Distribution Architecture

The system uses a single CloudFront distribution with two S3 origins: one for frontend static assets (`/frontend` prefix) and one for generated diagrams (`/diagrams` prefix). Origin Access Control (OAC) ensures S3 buckets remain private while CloudFront can access them.

**CloudFront and S3 Architecture**

```

```

Sources: [infrastructure/terraform/cloudfront.tf L72-L148](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L72-L148)

## Origin Access Control (OAC)

CloudFront uses OAC to securely access S3 without making the bucket public. This replaces the legacy Origin Access Identity (OAI) approach.

**OAC Configuration:**

| Property | Value | Purpose |
| --- | --- | --- |
| `name` | `${var.project_name}-oac-${var.environment}` | Unique identifier |
| `origin_access_control_origin_type` | `s3` | Specifies S3 as origin type |
| `signing_behavior` | `always` | Always sign requests to S3 |
| `signing_protocol` | `sigv4` | Use AWS Signature Version 4 |

The OAC resource is defined at [infrastructure/terraform/cloudfront.tf L8-L14](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L8-L14)

 and referenced by both origins in the distribution configuration.

**S3 Bucket Policy Integration:**

The bucket policy grants `s3:GetObject` permission only to requests from the CloudFront distribution ARN:

```
Condition = {
  StringEquals = {
    "AWS:SourceArn" = aws_cloudfront_distribution.frontend.arn
  }
}
```

This ensures all public access goes through CloudFront, enabling caching, compression, and HTTPS enforcement.

Sources: [infrastructure/terraform/cloudfront.tf L8-L14](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L8-L14)

 [infrastructure/terraform/cloudfront.tf L155-L178](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L155-L178)

## Cache Policies

The system defines two separate cache policies optimized for different content types.

**Cache Policy Comparison:**

| Property | `frontend_cache` | `diagrams_cache` |
| --- | --- | --- |
| **Resource** | `aws_cloudfront_cache_policy.frontend_cache` | `aws_cloudfront_cache_policy.diagrams_cache` |
| **min_ttl** | 3600 (1 hour) | 0 |
| **default_ttl** | 86400 (1 day) | 3600 (1 hour) |
| **max_ttl** | 604800 (7 days) | 86400 (1 day) |
| **Purpose** | Immutable frontend assets | Frequently updated diagrams |
| **Compression** | Brotli + Gzip | Brotli + Gzip |
| **Query Strings** | Ignored | Ignored |
| **Cookies** | Ignored | Ignored |
| **Headers** | None forwarded | None forwarded |

The frontend cache policy uses longer TTLs because React build assets include content hashes in filenames (e.g., `main.abc123.js`), making them effectively immutable. Diagram cache policy uses shorter TTLs to balance performance with freshness for newly generated content.

Both policies enable `enable_accept_encoding_brotli` and `enable_accept_encoding_gzip` for automatic compression, reducing bandwidth costs and improving load times.

Sources: [infrastructure/terraform/cloudfront.tf L20-L64](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L20-L64)

## CloudFront Distribution Configuration

**Distribution Origins:**

```

```

The distribution uses two origins from the same S3 bucket with different `origin_path` values:

* **S3-frontend**: Points to `/frontend` subdirectory for SPA assets
* **S3-diagrams**: Points to bucket root for `/diagrams` access

Sources: [infrastructure/terraform/cloudfront.tf L80-L93](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L80-L93)

**Distribution Settings:**

| Property | Value | Rationale |
| --- | --- | --- |
| `enabled` | `true` | Distribution is active |
| `is_ipv6_enabled` | `true` | Support modern networks |
| `default_root_object` | `index.html` | SPA entry point |
| `price_class` | `PriceClass_100` | North America + Europe only |
| `viewer_protocol_policy` | `redirect-to-https` | Force HTTPS for security |
| `minimum_protocol_version` | `TLSv1.2_2021` | Modern TLS only |

The `PriceClass_100` setting optimizes cost by using only North American and European edge locations, suitable for the expected user base.

Sources: [infrastructure/terraform/cloudfront.tf L72-L148](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L72-L148)

## Cache Behaviors and Path Routing

CloudFront uses ordered cache behaviors to route requests to appropriate origins with optimized caching strategies.

**Cache Behavior Decision Flow:**

```

```

**Behavior Configuration Details:**

1. **Default Behavior** [infrastructure/terraform/cloudfront.tf L96-L105](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L96-L105) * Serves SPA files from `/frontend` origin path * Uses `frontend_cache` policy (1 day default TTL) * Allows `GET`, `HEAD`, `OPTIONS` methods * Serves `index.html` as root object
2. **`/diagrams/*` Behavior** [infrastructure/terraform/cloudfront.tf L108-L116](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L108-L116) * Routes to S3-diagrams origin (bucket root) * Uses `diagrams_cache` policy (1 hour default TTL) * Handles PNG and markdown file requests * Pattern: `/diagrams/{chatId}.png`, `/diagrams/{chatId}.md`
3. **`/static/*` Behavior** [infrastructure/terraform/cloudfront.tf L119-L127](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L119-L127) * Routes to S3-frontend origin * Serves Vite-generated assets with content hashes * Uses `frontend_cache` policy (7 day max TTL) * Example paths: `/static/assets/main.abc123.js`

The ordered behaviors are evaluated top-to-bottom. Requests not matching ordered patterns fall through to the default behavior.

Sources: [infrastructure/terraform/cloudfront.tf L96-L127](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L96-L127)

## S3 Bucket Policy for CloudFront Access

The S3 bucket policy implements least-privilege access, allowing only the CloudFront service principal to read objects.

**Policy Structure:**

```

```

**Key Security Properties:**

* **Principal**: `Service: cloudfront.amazonaws.com` (not a user or role)
* **Action**: Only `s3:GetObject` (read-only, no write/delete)
* **Resource**: `${aws_s3_bucket.main.arn}/*` (all objects in bucket)
* **Condition**: `AWS:SourceArn` must match the specific CloudFront distribution ARN

This prevents:

* Direct public access to S3 objects
* Access from other CloudFront distributions
* Write operations through CloudFront

The policy depends on the CloudFront distribution resource to ensure creation order: `depends_on = [aws_cloudfront_distribution.frontend]`

Sources: [infrastructure/terraform/cloudfront.tf L155-L178](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L155-L178)

## Integration with Backend Lambda Functions

Backend Lambda functions generate CloudFront URLs when storing diagram files to S3.

**URL Generation Flow:**

```

```

**S3Helper URL Construction:**

The `S3Helper` class reads the `CLOUDFRONT_URL` environment variable (set by Terraform outputs) and constructs URLs:

```

```

**Key Methods:**

* `put_diagram_image(chat_id, image_data)` [src/backend/shared/aws_helpers.py L230-L256](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/shared/aws_helpers.py#L230-L256) * Uploads PNG to `diagrams/{chatId}.png` * Sets `ContentType: image/png` * Returns `https://{cloudfront_url}/diagrams/{chatId}.png`
* `put_diagram_markdown(chat_id, mermaid_code)` [src/backend/shared/aws_helpers.py L214-L228](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/shared/aws_helpers.py#L214-L228) * Uploads markdown to `diagrams/{chatId}.md` * Sets `ContentType: text/plain; charset=utf-8` * Wraps mermaid code in ````mermaid` blocks * Returns `https://{cloudfront_url}/diagrams/{chatId}.md`

The Lambda function receives these URLs and includes them in the API response to the frontend, which then uses them in the `DownloadButtons` component.

Sources: [src/backend/shared/aws_helpers.py L147-L269](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/shared/aws_helpers.py#L147-L269)

## Frontend Integration and File Downloads

The React frontend consumes CloudFront URLs for displaying and downloading diagrams.

**Download Flow:**

```

```

**Content-Type Validation:**

The `downloadFile` function validates that CloudFront returns the expected content type and not HTML (which would indicate a caching issue):

```

```

This validation catches cases where CloudFront might incorrectly cache the SPA `index.html` for diagram URLs due to misconfiguration.

**CORS Configuration:**

The fetch request uses `mode: 'cors'` to allow cross-origin requests from the React dev server during development and ensures proper CORS headers from CloudFront.

Sources: [src/frontend/src/components/DownloadButtons.tsx L21-L61](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/src/components/DownloadButtons.tsx#L21-L61)

## Cache Invalidation Strategy

Cache invalidation is handled by the deployment script after uploading new frontend assets.

**Invalidation Process:**

| Phase | Action | Files Affected |
| --- | --- | --- |
| **1. Upload** | `aws s3 sync` to `/frontend` prefix | All SPA assets |
| **2. Invalidate** | `aws cloudfront create-invalidation` | `/*` (all paths) |
| **3. Wait** | Poll invalidation status | N/A |
| **4. Complete** | New frontend immediately available | All edge locations updated |

The deployment script invalidates the entire distribution (`--paths "/*"`) to ensure:

* Updated `index.html` is served immediately
* New asset bundles with updated hashes are available
* Old cached versions don't persist

For diagram files (`/diagrams/*`), invalidation is not typically needed because:

* Each diagram uses a unique `chatId` in the filename
* New diagrams get new UUIDs, creating unique URLs
* Old diagrams remain cached without conflicts

**Invalidation Cost Consideration:**

CloudFront provides 1,000 free invalidation paths per month. The `/*` wildcard counts as one path. Frequent deployments should consider:

* Using versioned paths for frontend assets (already implemented via Vite content hashes)
* Only invalidating `index.html` specifically for minor updates
* Leveraging cache-busting query parameters for testing

Sources: Deployment script integration described in [Deployment Script](/dotpep/architecture-ai-assistant/6.1-deployment-script)

## CloudFront URL Structure

**Complete URL Patterns:**

| URL Pattern | Origin | Cache Policy | TTL | Example |
| --- | --- | --- | --- | --- |
| `https://{cloudfront_domain}/` | S3-frontend | frontend_cache | 1 day | Root redirects to index.html |
| `https://{cloudfront_domain}/index.html` | S3-frontend | frontend_cache | 1 day | SPA entry point |
| `https://{cloudfront_domain}/static/assets/*.js` | S3-frontend | frontend_cache | 7 days | Hashed JS bundles |
| `https://{cloudfront_domain}/static/assets/*.css` | S3-frontend | frontend_cache | 7 days | Hashed CSS bundles |
| `https://{cloudfront_domain}/diagrams/{uuid}.png` | S3-diagrams | diagrams_cache | 1 hour | Generated diagram images |
| `https://{cloudfront_domain}/diagrams/{uuid}.md` | S3-diagrams | diagrams_cache | 1 hour | Diagram markdown source |

All URLs enforce HTTPS via `viewer_protocol_policy = "redirect-to-https"`. HTTP requests receive a 301 redirect to the HTTPS equivalent.

**Compression Behavior:**

CloudFront automatically compresses responses when:

1. `Accept-Encoding` header includes `gzip` or `br` (brotli)
2. File size is between 1KB and 10MB
3. Content-Type is compressible (text/html, text/css, application/javascript, etc.)

PNG files (`image/png`) are not compressed as they are already binary-compressed format.

Sources: [infrastructure/terraform/cloudfront.tf L72-L148](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L72-L148)