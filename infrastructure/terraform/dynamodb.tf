# Architecture AI Assistant - DynamoDB Configuration
# Requirements: 4.1, 6.1

resource "aws_dynamodb_table" "chat_history" {
  name         = "${var.project_name}-${var.dynamodb_table_name}-${var.environment}"
  billing_mode = "PAY_PER_REQUEST" # On-demand capacity mode

  # Primary key: chatId (partition key) + timestamp (sort key)
  hash_key  = "chatId"
  range_key = "timestamp"

  # Key attributes - DynamoDB only requires key attributes to be defined
  # Non-key attributes (userMessage, diagramType, aiResponse, mermaidCode, 
  # diagramImageS3Key, diagramMarkdownS3Key, imageUrl, markdownUrl, status)
  # are schemaless and don't need to be declared

  attribute {
    name = "chatId"
    type = "S" # String - UUID for the chat entry
  }

  attribute {
    name = "timestamp"
    type = "N" # Number - Unix timestamp for sorting
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
