# Architecture AI Assistant - IAM Roles and Policies
# Requirements: 6.3 - Least-privilege permissions for Lambda functions

# Lambda execution role assume policy
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# IAM Role for generate_diagram Lambda
resource "aws_iam_role" "lambda_generate_diagram" {
  name               = "${var.project_name}-lambda-generate-diagram-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# IAM Role for chat_crud Lambda
resource "aws_iam_role" "lambda_chat_crud" {
  name               = "${var.project_name}-lambda-chat-crud-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# IAM Role for get_history Lambda
resource "aws_iam_role" "lambda_get_history" {
  name               = "${var.project_name}-lambda-get-history-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# IAM Role for session_crud Lambda
resource "aws_iam_role" "lambda_session_crud" {
  name               = "${var.project_name}-lambda-session-crud-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# CloudWatch Logs policy for all Lambda functions
data "aws_iam_policy_document" "lambda_cloudwatch_logs" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}


resource "aws_iam_policy" "lambda_cloudwatch_logs" {
  name        = "${var.project_name}-lambda-cloudwatch-logs-${var.environment}"
  description = "Allow Lambda functions to write CloudWatch logs"
  policy      = data.aws_iam_policy_document.lambda_cloudwatch_logs.json
}

# DynamoDB policy for generate_diagram Lambda (PutItem, GetItem)
data "aws_iam_policy_document" "generate_diagram_dynamodb" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem"
    ]
    resources = [aws_dynamodb_table.chat_history.arn]
  }
}

resource "aws_iam_policy" "generate_diagram_dynamodb" {
  name        = "${var.project_name}-generate-diagram-dynamodb-${var.environment}"
  description = "Allow generate_diagram Lambda to write to DynamoDB"
  policy      = data.aws_iam_policy_document.generate_diagram_dynamodb.json
}

# S3 policy for generate_diagram Lambda (PutObject for diagrams)
data "aws_iam_policy_document" "generate_diagram_s3" {
  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject"
    ]
    resources = ["${aws_s3_bucket.main.arn}/diagrams/*"]
  }
}

resource "aws_iam_policy" "generate_diagram_s3" {
  name        = "${var.project_name}-generate-diagram-s3-${var.environment}"
  description = "Allow generate_diagram Lambda to write diagrams to S3"
  policy      = data.aws_iam_policy_document.generate_diagram_s3.json
}

# DynamoDB policy for chat_crud Lambda (PutItem)
data "aws_iam_policy_document" "chat_crud_dynamodb" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem"
    ]
    resources = [aws_dynamodb_table.chat_history.arn]
  }
}

resource "aws_iam_policy" "chat_crud_dynamodb" {
  name        = "${var.project_name}-chat-crud-dynamodb-${var.environment}"
  description = "Allow chat_crud Lambda to perform CRUD on DynamoDB"
  policy      = data.aws_iam_policy_document.chat_crud_dynamodb.json
}

# DynamoDB policy for get_history Lambda (Query)
data "aws_iam_policy_document" "get_history_dynamodb" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:GetItem"
    ]
    resources = [
      aws_dynamodb_table.chat_history.arn,
      "${aws_dynamodb_table.chat_history.arn}/index/*"
    ]
  }
}

resource "aws_iam_policy" "get_history_dynamodb" {
  name        = "${var.project_name}-get-history-dynamodb-${var.environment}"
  description = "Allow get_history Lambda to query DynamoDB"
  policy      = data.aws_iam_policy_document.get_history_dynamodb.json
}

# DynamoDB policy for session_crud Lambda (Full CRUD + Query)
data "aws_iam_policy_document" "session_crud_dynamodb" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ]
    resources = [
      aws_dynamodb_table.chat_history.arn,
      "${aws_dynamodb_table.chat_history.arn}/index/*"
    ]
  }
}

resource "aws_iam_policy" "session_crud_dynamodb" {
  name        = "${var.project_name}-session-crud-dynamodb-${var.environment}"
  description = "Allow session_crud Lambda to perform CRUD and query operations on DynamoDB"
  policy      = data.aws_iam_policy_document.session_crud_dynamodb.json
}

# Attach policies to generate_diagram Lambda role
resource "aws_iam_role_policy_attachment" "generate_diagram_cloudwatch" {
  role       = aws_iam_role.lambda_generate_diagram.name
  policy_arn = aws_iam_policy.lambda_cloudwatch_logs.arn
}

resource "aws_iam_role_policy_attachment" "generate_diagram_dynamodb" {
  role       = aws_iam_role.lambda_generate_diagram.name
  policy_arn = aws_iam_policy.generate_diagram_dynamodb.arn
}

resource "aws_iam_role_policy_attachment" "generate_diagram_s3" {
  role       = aws_iam_role.lambda_generate_diagram.name
  policy_arn = aws_iam_policy.generate_diagram_s3.arn
}

# Attach policies to chat_crud Lambda role
resource "aws_iam_role_policy_attachment" "chat_crud_cloudwatch" {
  role       = aws_iam_role.lambda_chat_crud.name
  policy_arn = aws_iam_policy.lambda_cloudwatch_logs.arn
}

resource "aws_iam_role_policy_attachment" "chat_crud_dynamodb" {
  role       = aws_iam_role.lambda_chat_crud.name
  policy_arn = aws_iam_policy.chat_crud_dynamodb.arn
}

# Attach policies to get_history Lambda role
resource "aws_iam_role_policy_attachment" "get_history_cloudwatch" {
  role       = aws_iam_role.lambda_get_history.name
  policy_arn = aws_iam_policy.lambda_cloudwatch_logs.arn
}

resource "aws_iam_role_policy_attachment" "get_history_dynamodb" {
  role       = aws_iam_role.lambda_get_history.name
  policy_arn = aws_iam_policy.get_history_dynamodb.arn
}

# Attach policies to session_crud Lambda role
resource "aws_iam_role_policy_attachment" "session_crud_cloudwatch" {
  role       = aws_iam_role.lambda_session_crud.name
  policy_arn = aws_iam_policy.lambda_cloudwatch_logs.arn
}

resource "aws_iam_role_policy_attachment" "session_crud_dynamodb" {
  role       = aws_iam_role.lambda_session_crud.name
  policy_arn = aws_iam_policy.session_crud_dynamodb.arn
}
