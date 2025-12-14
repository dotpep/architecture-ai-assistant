# Architecture AI Assistant - CloudFront Configuration
# Requirements: 6.4, 8.2

# ============================================
# Origin Access Control for S3
# ============================================

resource "aws_cloudfront_origin_access_control" "main" {
  name                              = "${var.project_name}-oac-${var.environment}"
  description                       = "OAC for Architecture AI Assistant S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# ============================================
# CloudFront Cache Policies
# ============================================

# Cache policy for static frontend assets (longer cache)
resource "aws_cloudfront_cache_policy" "frontend_cache" {
  name        = "${var.project_name}-frontend-cache-${var.environment}"
  comment     = "Cache policy for frontend static assets"
  default_ttl = 86400    # 1 day
  max_ttl     = 604800   # 7 days
  min_ttl     = 3600     # 1 hour

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    headers_config {
      header_behavior = "none"
    }
    query_strings_config {
      query_string_behavior = "none"
    }
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true
  }
}

# Cache policy for diagram files (moderate cache)
resource "aws_cloudfront_cache_policy" "diagrams_cache" {
  name        = "${var.project_name}-diagrams-cache-${var.environment}"
  comment     = "Cache policy for generated diagram files"
  default_ttl = 3600     # 1 hour
  max_ttl     = 86400    # 1 day
  min_ttl     = 0

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    headers_config {
      header_behavior = "none"
    }
    query_strings_config {
      query_string_behavior = "none"
    }
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true
  }
}


# ============================================
# CloudFront Distribution
# Requirements: 6.4, 8.2
# ============================================

resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  comment             = "Architecture AI Assistant - Frontend and Diagrams CDN"
  price_class         = "PriceClass_100" # Use only North America and Europe edge locations

  # S3 Origin for frontend static files
  origin {
    domain_name              = aws_s3_bucket.main.bucket_regional_domain_name
    origin_id                = "S3-frontend"
    origin_access_control_id = aws_cloudfront_origin_access_control.main.id
    origin_path              = "/frontend"
  }

  # S3 Origin for diagram files
  origin {
    domain_name              = aws_s3_bucket.main.bucket_regional_domain_name
    origin_id                = "S3-diagrams"
    origin_access_control_id = aws_cloudfront_origin_access_control.main.id
    origin_path              = "/diagrams"
  }

  # Default cache behavior for frontend (SPA)
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-frontend"
    cache_policy_id        = aws_cloudfront_cache_policy.frontend_cache.id
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    # Function associations for SPA routing could be added here
  }

  # Cache behavior for diagram files (/diagrams/*)
  ordered_cache_behavior {
    path_pattern           = "/diagrams/*"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-diagrams"
    cache_policy_id        = aws_cloudfront_cache_policy.diagrams_cache.id
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
  }

  # Cache behavior for static assets (JS, CSS, images)
  ordered_cache_behavior {
    path_pattern           = "/static/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-frontend"
    cache_policy_id        = aws_cloudfront_cache_policy.frontend_cache.id
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
  }

  # Custom error response for SPA routing - 404 returns index.html
  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }

  # Custom error response for SPA routing - 403 returns index.html
  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }

  # No geographic restrictions
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # Use default CloudFront certificate (HTTPS enabled)
  viewer_certificate {
    cloudfront_default_certificate = true
    minimum_protocol_version       = "TLSv1.2_2021"
  }

  tags = {
    Name = "${var.project_name}-cloudfront"
  }
}


# ============================================
# S3 Bucket Policy for CloudFront Access
# ============================================

resource "aws_s3_bucket_policy" "main" {
  bucket = aws_s3_bucket.main.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontServicePrincipal"
        Effect    = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.main.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.frontend.arn
          }
        }
      }
    ]
  })

  depends_on = [aws_cloudfront_distribution.frontend]
}
