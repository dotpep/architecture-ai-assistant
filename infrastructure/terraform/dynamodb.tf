# Architecture AI Assistant - DynamoDB Configuration
# Requirements: 4.1, 6.1
# Note: Full implementation in Task 2.1

resource "aws_dynamodb_table" "chat_history" {
  name         = "${var.project_name}-${var.dynamodb_table_name}-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "chatId"
  range_key    = "timestamp"

  attribute {
    name = "chatId"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  tags = {
    Name = "${var.project_name}-chat-history"
  }
}
