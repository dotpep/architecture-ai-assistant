# Architecture AI Assistant - Lambda Functions Configuration
# Requirements: 6.1, 6.3

# ============================================
# Lambda Layer for Shared Dependencies
# ============================================

# Placeholder for Lambda layer (will be replaced during deployment)
data "archive_file" "lambda_layer_placeholder" {
  type        = "zip"
  output_path = "${path.module}/lambda_layer_placeholder.zip"

  source {
    content  = "# Placeholder for shared dependencies"
    filename = "python/placeholder.py"
  }
}

# Lambda layer for shared Python dependencies
resource "aws_lambda_layer_version" "shared_dependencies" {
  layer_name          = "${var.project_name}-shared-deps-${var.environment}"
  description         = "Shared Python dependencies for Lambda functions"
  filename            = data.archive_file.lambda_layer_placeholder.output_path
  source_code_hash    = data.archive_file.lambda_layer_placeholder.output_base64sha256
  compatible_runtimes = ["python3.11"]

  lifecycle {
    create_before_destroy = true
  }
}

# ============================================
# Placeholder Zip for Lambda Functions
# ============================================

# Placeholder zip for Lambda functions (will be replaced during deployment)
data "archive_file" "lambda_placeholder" {
  type        = "zip"
  output_path = "${path.module}/lambda_placeholder.zip"

  source {
    content  = <<-EOF
import json

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps({'message': 'Placeholder - deploy actual function code'})
    }
EOF
    filename = "lambda_function.py"
  }
}


# ============================================
# Generate Diagram Lambda Function
# Requirements: 6.1, 6.3, 7.1
# Timeout: 60s, Memory: 512MB (for LLM API calls)
# ============================================

resource "aws_lambda_function" "generate_diagram" {
  function_name = "${var.project_name}-generate-diagram-${var.environment}"
  description   = "Generates architecture diagrams using LLM API"
  role          = aws_iam_role.lambda_generate_diagram.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.11"
  timeout       = 60  # 60 seconds for LLM API calls
  memory_size   = 512 # 512MB for processing

  filename         = data.archive_file.lambda_placeholder.output_path
  source_code_hash = data.archive_file.lambda_placeholder.output_base64sha256

  layers = [aws_lambda_layer_version.shared_dependencies.arn]

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.chat_history.name
      S3_BUCKET_NAME      = aws_s3_bucket.main.id
      CLOUDFRONT_URL      = "https://${aws_cloudfront_distribution.frontend.domain_name}"
      LLM_API_ENDPOINT    = var.llm_api_endpoint
      LLM_API_KEY         = var.llm_api_key
      ENVIRONMENT         = var.environment
    }
  }

  tags = {
    Name     = "${var.project_name}-generate-diagram"
    Function = "diagram-generation"
  }
}

# CloudWatch Log Group for generate_diagram Lambda
resource "aws_cloudwatch_log_group" "generate_diagram" {
  name              = "/aws/lambda/${aws_lambda_function.generate_diagram.function_name}"
  retention_in_days = 14

  tags = {
    Name = "${var.project_name}-generate-diagram-logs"
  }
}

# ============================================
# Chat CRUD Lambda Function
# Requirements: 6.1, 6.3, 7.3
# Timeout: 10s, Memory: 256MB
# ============================================

resource "aws_lambda_function" "chat_crud" {
  function_name = "${var.project_name}-chat-crud-${var.environment}"
  description   = "Handles chat message CRUD operations"
  role          = aws_iam_role.lambda_chat_crud.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.11"
  timeout       = 10  # 10 seconds for DynamoDB operations
  memory_size   = 256 # 256MB for basic operations

  filename         = data.archive_file.lambda_placeholder.output_path
  source_code_hash = data.archive_file.lambda_placeholder.output_base64sha256

  layers = [aws_lambda_layer_version.shared_dependencies.arn]

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.chat_history.name
      ENVIRONMENT         = var.environment
    }
  }

  tags = {
    Name     = "${var.project_name}-chat-crud"
    Function = "chat-operations"
  }
}

# CloudWatch Log Group for chat_crud Lambda
resource "aws_cloudwatch_log_group" "chat_crud" {
  name              = "/aws/lambda/${aws_lambda_function.chat_crud.function_name}"
  retention_in_days = 14

  tags = {
    Name = "${var.project_name}-chat-crud-logs"
  }
}

# ============================================
# Get History Lambda Function
# Requirements: 6.1, 6.3, 7.2
# Timeout: 10s, Memory: 256MB
# ============================================

resource "aws_lambda_function" "get_history" {
  function_name = "${var.project_name}-get-history-${var.environment}"
  description   = "Retrieves chat history with pagination"
  role          = aws_iam_role.lambda_get_history.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.11"
  timeout       = 10  # 10 seconds for DynamoDB queries
  memory_size   = 256 # 256MB for query operations

  filename         = data.archive_file.lambda_placeholder.output_path
  source_code_hash = data.archive_file.lambda_placeholder.output_base64sha256

  layers = [aws_lambda_layer_version.shared_dependencies.arn]

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.chat_history.name
      ENVIRONMENT         = var.environment
    }
  }

  tags = {
    Name     = "${var.project_name}-get-history"
    Function = "history-retrieval"
  }
}

# CloudWatch Log Group for get_history Lambda
resource "aws_cloudwatch_log_group" "get_history" {
  name              = "/aws/lambda/${aws_lambda_function.get_history.function_name}"
  retention_in_days = 14

  tags = {
    Name = "${var.project_name}-get-history-logs"
  }
}
