# Architecture AI Assistant - Input Variables
# Requirements: 6.1, 6.2

variable "aws_region" {
  description = "AWS region for deploying resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "architecture-ai-assistant"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for frontend and diagrams"
  type        = string
  default     = "architecture-ai-assistant-bucket"
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table for chat history"
  type        = string
  default     = "chat_history"
}

variable "llm_api_endpoint" {
  description = "LLM API endpoint URL"
  type        = string
  sensitive   = true
  default     = ""
}

variable "llm_api_key" {
  description = "LLM API authentication key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "llm_model" {
  description = "LLM model name to use for generation"
  type        = string
  default     = "llama-3.3-70b-versatile"
}
