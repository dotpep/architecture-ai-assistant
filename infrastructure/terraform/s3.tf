# Architecture AI Assistant - S3 Configuration
# Requirements: 3.1, 3.2, 6.4

# Main S3 bucket for frontend static files and diagram storage
resource "aws_s3_bucket" "main" {
  bucket = "${var.s3_bucket_name}-${var.environment}"

  tags = {
    Name        = "${var.project_name}-bucket"
    Description = "Stores frontend assets and generated diagrams"
  }
}

# Block all public access - CloudFront will serve content
resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable static website hosting for SPA routing
resource "aws_s3_bucket_website_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

# Enable versioning for diagram files protection
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption configuration
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# CORS configuration for frontend API calls
resource "aws_s3_bucket_cors_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"] # Allow all origins during development (Requirement 6.5)
    expose_headers  = ["ETag"]
    max_age_seconds = 3600
  }
}

# Lifecycle rules for diagram storage management
resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  # Rule for diagram files - transition to cheaper storage after 30 days
  rule {
    id     = "diagrams-lifecycle"
    status = "Enabled"

    filter {
      prefix = "diagrams/"
    }

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Keep old versions for 90 days
    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }

  # Rule for frontend assets - expire old versions after 7 days
  rule {
    id     = "frontend-lifecycle"
    status = "Enabled"

    filter {
      prefix = "frontend/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

# S3 bucket structure follows design document:
# s3://architecture-ai-bucket/
# ├── frontend/
# │   ├── index.html
# │   ├── static/
# │   │   ├── js/
# │   │   └── css/
# │   └── assets/
# └── diagrams/
#     ├── {chatId}.md
#     ├── {chatId}.png
#     └── ...
