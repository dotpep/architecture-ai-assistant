# Architecture AI Assistant - S3 Configuration
# Requirements: 3.1, 3.2, 6.4
# Note: Full implementation in Task 2.2

resource "aws_s3_bucket" "main" {
  bucket = "${var.s3_bucket_name}-${var.environment}"

  tags = {
    Name = "${var.project_name}-bucket"
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_website_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}
