# Architecture AI Assistant - DynamoDB Configuration
# Requirements: 4.1, 6.1, 2.1 (Session Management), 5.2 (Session Listing)

resource "aws_dynamodb_table" "chat_history" {
  name         = "${var.project_name}-${var.dynamodb_table_name}-${var.environment}"
  billing_mode = "PAY_PER_REQUEST" # On-demand capacity mode

  # Primary key: PK (partition key) + SK (sort key) for single-table design
  # PK format: SESSION#{sessionId}
  # SK format: METADATA for session info, MSG#{timestamp} for messages
  hash_key  = "PK"
  range_key = "SK"

  # Key attributes - DynamoDB only requires key attributes to be defined
  # Non-key attributes (sessionId, messageId, title, userMessage, diagramType, 
  # aiResponse, mermaidCode, diagramImageS3Key, diagramMarkdownS3Key, 
  # imageUrl, markdownUrl, status, createdAt, updatedAt, messageCount)
  # are schemaless and don't need to be declared

  attribute {
    name = "PK"
    type = "S" # String - Partition key for single-table design
  }

  attribute {
    name = "SK"
    type = "S" # String - Sort key for single-table design
  }

  attribute {
    name = "createdAt"
    type = "N" # Number - Unix timestamp for session creation
  }

  # Global Secondary Index for listing sessions by creation date
  global_secondary_index {
    name            = "SessionsByCreatedAt"
    hash_key        = "SK"
    range_key       = "createdAt"
    projection_type = "ALL"
  }

  # Enable point-in-time recovery for data protection
  point_in_time_recovery {
    enabled = true
  }

  # Enable server-side encryption
  server_side_encryption {
    enabled = true
  }

  # Time-to-live attribute for optional data expiration
  ttl {
    attribute_name = "expiresAt"
    enabled        = true
  }

  tags = {
    Name        = "${var.project_name}-chat-history"
    Description = "Stores chat history and diagram metadata"
  }
}
