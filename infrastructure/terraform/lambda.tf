# Architecture AI Assistant - Lambda Functions Configuration
# Requirements: 6.1, 6.3
# Note: Full implementation in Task 3.2

# Placeholder zip for Lambda functions (will be replaced during deployment)
data "archive_file" "lambda_placeholder" {
  type        = "zip"
  output_path = "${path.module}/lambda_placeholder.zip"

  source {
    content  = "# Placeholder - will be replaced during deployment"
    filename = "lambda_function.py"
  }
}

# Generate Diagram Lambda Function
resource "aws_lambda_function" "generate_diagram" {
  function_name = "${var.project_name}-generate-diagram-${var.environment}"
  role          = aws_iam_role.lambda_generate_diagram.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.11"
  timeout       = 60
  memory_size   = 512

  filename         = data.archive_file.lambda_placeholder.output_path
  source_code_hash = data.archive_file.lambda_placeholder.output_base64sha256

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.chat_history.name
      S3_BUCKET_NAME      = aws_s3_bucket.main.id
      LLM_API_ENDPOINT    = var.llm_api_endpoint
      LLM_API_KEY         = var.llm_api_key
      ENVIRONMENT         = var.environment
    }
  }

  tags = {
    Name = "${var.project_name}-generate-diagram"
  }
}

# Chat CRUD Lambda Function
resource "aws_lambda_function" "chat_crud" {
  function_name = "${var.project_name}-chat-crud-${var.environment}"
  role          = aws_iam_role.lambda_chat_crud.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.11"
  timeout       = 10
  memory_size   = 256

  filename         = data.archive_file.lambda_placeholder.output_path
  source_code_hash = data.archive_file.lambda_placeholder.output_base64sha256

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.chat_history.name
      ENVIRONMENT         = var.environment
    }
  }

  tags = {
    Name = "${var.project_name}-chat-crud"
  }
}

# Get History Lambda Function
resource "aws_lambda_function" "get_history" {
  function_name = "${var.project_name}-get-history-${var.environment}"
  role          = aws_iam_role.lambda_get_history.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.11"
  timeout       = 10
  memory_size   = 256

  filename         = data.archive_file.lambda_placeholder.output_path
  source_code_hash = data.archive_file.lambda_placeholder.output_base64sha256

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.chat_history.name
      ENVIRONMENT         = var.environment
    }
  }

  tags = {
    Name = "${var.project_name}-get-history"
  }
}
