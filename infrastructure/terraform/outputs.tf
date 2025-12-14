# Architecture AI Assistant - Terraform Outputs
# Requirements: 6.2

output "cloudfront_url" {
  description = "CloudFront distribution URL for the frontend"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID for cache invalidation"
  value       = aws_cloudfront_distribution.frontend.id
}

output "api_gateway_url" {
  description = "API Gateway invoke URL"
  value       = aws_api_gateway_stage.main.invoke_url
}

output "api_gateway_id" {
  description = "API Gateway REST API ID"
  value       = aws_api_gateway_rest_api.main.id
}

output "s3_bucket_name" {
  description = "S3 bucket name for frontend and diagrams"
  value       = aws_s3_bucket.main.id
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.main.arn
}

output "dynamodb_table_name" {
  description = "DynamoDB table name for chat history"
  value       = aws_dynamodb_table.chat_history.name
}

output "dynamodb_table_arn" {
  description = "DynamoDB table ARN"
  value       = aws_dynamodb_table.chat_history.arn
}

output "lambda_generate_diagram_arn" {
  description = "ARN of the generate_diagram Lambda function"
  value       = aws_lambda_function.generate_diagram.arn
}

output "lambda_chat_crud_arn" {
  description = "ARN of the chat_crud Lambda function"
  value       = aws_lambda_function.chat_crud.arn
}

output "lambda_get_history_arn" {
  description = "ARN of the get_history Lambda function"
  value       = aws_lambda_function.get_history.arn
}
