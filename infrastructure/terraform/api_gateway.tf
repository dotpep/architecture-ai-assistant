# Architecture AI Assistant - API Gateway Configuration
# Requirements: 6.5, 7.1, 7.2, 7.3

# REST API Definition
resource "aws_api_gateway_rest_api" "main" {
  name        = "${var.project_name}-api-${var.environment}"
  description = "API Gateway for Architecture AI Assistant"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name = "${var.project_name}-api"
  }
}

# /api resource
resource "aws_api_gateway_resource" "api" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "api"
}

# /api/diagram resource
resource "aws_api_gateway_resource" "diagram" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "diagram"
}

# /api/diagram/generate resource
resource "aws_api_gateway_resource" "diagram_generate" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.diagram.id
  path_part   = "generate"
}

# /api/chat resource
resource "aws_api_gateway_resource" "chat" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "chat"
}

# /api/chat/history resource
resource "aws_api_gateway_resource" "chat_history" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.chat.id
  path_part   = "history"
}

# /api/chat/save resource
resource "aws_api_gateway_resource" "chat_save" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.chat.id
  path_part   = "save"
}

# /api/session resource
resource "aws_api_gateway_resource" "session" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "session"
}

# /api/session/{sessionId} resource
resource "aws_api_gateway_resource" "session_id" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.session.id
  path_part   = "{sessionId}"
}

# /api/session/{sessionId}/messages resource
resource "aws_api_gateway_resource" "session_messages" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.session_id.id
  path_part   = "messages"
}


# ============================================
# POST /api/diagram/generate - Generate Diagram
# Requirements: 7.1
# ============================================

# POST method for diagram generation
resource "aws_api_gateway_method" "diagram_generate_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.diagram_generate.id
  http_method   = "POST"
  authorization = "NONE"
}

# Lambda integration for diagram generation
resource "aws_api_gateway_integration" "diagram_generate_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.diagram_generate.id
  http_method             = aws_api_gateway_method.diagram_generate_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.generate_diagram.invoke_arn
}

# Method response for diagram generation POST
resource "aws_api_gateway_method_response" "diagram_generate_post_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.diagram_generate.id
  http_method = aws_api_gateway_method.diagram_generate_post.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# Integration response for diagram generation POST
resource "aws_api_gateway_integration_response" "diagram_generate_post_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.diagram_generate.id
  http_method = aws_api_gateway_method.diagram_generate_post.http_method
  status_code = aws_api_gateway_method_response.diagram_generate_post_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}



# CORS OPTIONS for diagram/generate
resource "aws_api_gateway_method" "diagram_generate_options" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.diagram_generate.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "diagram_generate_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.diagram_generate.id
  http_method = aws_api_gateway_method.diagram_generate_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "diagram_generate_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.diagram_generate.id
  http_method = aws_api_gateway_method.diagram_generate_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "diagram_generate_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.diagram_generate.id
  http_method = aws_api_gateway_method.diagram_generate_options.http_method
  status_code = aws_api_gateway_method_response.diagram_generate_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}


# ============================================
# GET /api/chat/history - Get Chat History
# Requirements: 7.2
# ============================================

# GET method for chat history
resource "aws_api_gateway_method" "chat_history_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.chat_history.id
  http_method   = "GET"
  authorization = "NONE"
}

# Lambda integration for chat history
resource "aws_api_gateway_integration" "chat_history_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.chat_history.id
  http_method             = aws_api_gateway_method.chat_history_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_history.invoke_arn
}

# Method response for chat history GET
resource "aws_api_gateway_method_response" "chat_history_get_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_history.id
  http_method = aws_api_gateway_method.chat_history_get.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# Integration response for chat history GET
resource "aws_api_gateway_integration_response" "chat_history_get_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_history.id
  http_method = aws_api_gateway_method.chat_history_get.http_method
  status_code = aws_api_gateway_method_response.chat_history_get_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}

# CORS OPTIONS for chat/history
resource "aws_api_gateway_method" "chat_history_options" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.chat_history.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "chat_history_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_history.id
  http_method = aws_api_gateway_method.chat_history_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "chat_history_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_history.id
  http_method = aws_api_gateway_method.chat_history_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "chat_history_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_history.id
  http_method = aws_api_gateway_method.chat_history_options.http_method
  status_code = aws_api_gateway_method_response.chat_history_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}


# ============================================
# POST /api/chat/save - Save Chat Message
# Requirements: 7.3
# ============================================

# POST method for saving chat
resource "aws_api_gateway_method" "chat_save_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.chat_save.id
  http_method   = "POST"
  authorization = "NONE"
}

# Lambda integration for saving chat
resource "aws_api_gateway_integration" "chat_save_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.chat_save.id
  http_method             = aws_api_gateway_method.chat_save_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.chat_crud.invoke_arn
}

# Method response for chat save POST
resource "aws_api_gateway_method_response" "chat_save_post_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_save.id
  http_method = aws_api_gateway_method.chat_save_post.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# Integration response for chat save POST
resource "aws_api_gateway_integration_response" "chat_save_post_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_save.id
  http_method = aws_api_gateway_method.chat_save_post.http_method
  status_code = aws_api_gateway_method_response.chat_save_post_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}

# CORS OPTIONS for chat/save
resource "aws_api_gateway_method" "chat_save_options" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.chat_save.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "chat_save_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_save.id
  http_method = aws_api_gateway_method.chat_save_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "chat_save_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_save.id
  http_method = aws_api_gateway_method.chat_save_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "chat_save_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_save.id
  http_method = aws_api_gateway_method.chat_save_options.http_method
  status_code = aws_api_gateway_method_response.chat_save_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}


# ============================================
# POST /api/session - Create Session
# Requirements: 5.1
# ============================================

resource "aws_api_gateway_method" "session_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.session.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "session_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.session.id
  http_method             = aws_api_gateway_method.session_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.session_crud.invoke_arn
}

resource "aws_api_gateway_method_response" "session_post_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session.id
  http_method = aws_api_gateway_method.session_post.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_integration_response" "session_post_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session.id
  http_method = aws_api_gateway_method.session_post.http_method
  status_code = aws_api_gateway_method_response.session_post_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}

# CORS OPTIONS for /api/session
resource "aws_api_gateway_method" "session_options" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.session.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "session_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session.id
  http_method = aws_api_gateway_method.session_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "session_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session.id
  http_method = aws_api_gateway_method.session_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "session_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session.id
  http_method = aws_api_gateway_method.session_options.http_method
  status_code = aws_api_gateway_method_response.session_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}


# ============================================
# GET /api/session - List Sessions
# Requirements: 5.2
# ============================================

resource "aws_api_gateway_method" "session_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.session.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "session_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.session.id
  http_method             = aws_api_gateway_method.session_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.session_crud.invoke_arn
}

resource "aws_api_gateway_method_response" "session_get_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session.id
  http_method = aws_api_gateway_method.session_get.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_integration_response" "session_get_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session.id
  http_method = aws_api_gateway_method.session_get.http_method
  status_code = aws_api_gateway_method_response.session_get_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}


# ============================================
# GET /api/session/{sessionId} - Get Session
# Requirements: 5.1
# ============================================

resource "aws_api_gateway_method" "session_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.session_id.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "session_id_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.session_id.id
  http_method             = aws_api_gateway_method.session_id_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.session_crud.invoke_arn
}

resource "aws_api_gateway_method_response" "session_id_get_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_id.id
  http_method = aws_api_gateway_method.session_id_get.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_integration_response" "session_id_get_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_id.id
  http_method = aws_api_gateway_method.session_id_get.http_method
  status_code = aws_api_gateway_method_response.session_id_get_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}


# ============================================
# PUT /api/session/{sessionId} - Update Session
# Requirements: 5.1
# ============================================

resource "aws_api_gateway_method" "session_id_put" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.session_id.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "session_id_put" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.session_id.id
  http_method             = aws_api_gateway_method.session_id_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.session_crud.invoke_arn
}

resource "aws_api_gateway_method_response" "session_id_put_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_id.id
  http_method = aws_api_gateway_method.session_id_put.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_integration_response" "session_id_put_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_id.id
  http_method = aws_api_gateway_method.session_id_put.http_method
  status_code = aws_api_gateway_method_response.session_id_put_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}


# ============================================
# DELETE /api/session/{sessionId} - Delete Session
# Requirements: 5.1
# ============================================

resource "aws_api_gateway_method" "session_id_delete" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.session_id.id
  http_method   = "DELETE"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "session_id_delete" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.session_id.id
  http_method             = aws_api_gateway_method.session_id_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.session_crud.invoke_arn
}

resource "aws_api_gateway_method_response" "session_id_delete_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_id.id
  http_method = aws_api_gateway_method.session_id_delete.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_integration_response" "session_id_delete_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_id.id
  http_method = aws_api_gateway_method.session_id_delete.http_method
  status_code = aws_api_gateway_method_response.session_id_delete_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}

# CORS OPTIONS for /api/session/{sessionId}
resource "aws_api_gateway_method" "session_id_options" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.session_id.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "session_id_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_id.id
  http_method = aws_api_gateway_method.session_id_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "session_id_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_id.id
  http_method = aws_api_gateway_method.session_id_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "session_id_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_id.id
  http_method = aws_api_gateway_method.session_id_options.http_method
  status_code = aws_api_gateway_method_response.session_id_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}


# ============================================
# GET /api/session/{sessionId}/messages - Get Session Messages
# Requirements: 5.3
# ============================================

resource "aws_api_gateway_method" "session_messages_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.session_messages.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "session_messages_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.session_messages.id
  http_method             = aws_api_gateway_method.session_messages_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_history.invoke_arn
}

resource "aws_api_gateway_method_response" "session_messages_get_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_messages.id
  http_method = aws_api_gateway_method.session_messages_get.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_integration_response" "session_messages_get_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_messages.id
  http_method = aws_api_gateway_method.session_messages_get.http_method
  status_code = aws_api_gateway_method_response.session_messages_get_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}

# CORS OPTIONS for /api/session/{sessionId}/messages
resource "aws_api_gateway_method" "session_messages_options" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.session_messages.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "session_messages_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_messages.id
  http_method = aws_api_gateway_method.session_messages_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "session_messages_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_messages.id
  http_method = aws_api_gateway_method.session_messages_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "session_messages_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.session_messages.id
  http_method = aws_api_gateway_method.session_messages_options.http_method
  status_code = aws_api_gateway_method_response.session_messages_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}


# ============================================
# Lambda Permissions for API Gateway
# ============================================

# Permission for API Gateway to invoke generate_diagram Lambda
resource "aws_lambda_permission" "api_gateway_generate_diagram" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.generate_diagram.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# Permission for API Gateway to invoke chat_crud Lambda
resource "aws_lambda_permission" "api_gateway_chat_crud" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.chat_crud.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# Permission for API Gateway to invoke get_history Lambda
resource "aws_lambda_permission" "api_gateway_get_history" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_history.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# Permission for API Gateway to invoke session_crud Lambda
resource "aws_lambda_permission" "api_gateway_session_crud" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.session_crud.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# ============================================
# API Gateway Deployment and Stage
# ============================================

# API Gateway deployment
resource "aws_api_gateway_deployment" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.api.id,
      aws_api_gateway_resource.diagram.id,
      aws_api_gateway_resource.diagram_generate.id,
      aws_api_gateway_resource.chat.id,
      aws_api_gateway_resource.chat_history.id,
      aws_api_gateway_resource.chat_save.id,
      aws_api_gateway_resource.session.id,
      aws_api_gateway_resource.session_id.id,
      aws_api_gateway_resource.session_messages.id,
      aws_api_gateway_method.diagram_generate_post.id,
      aws_api_gateway_method.chat_history_get.id,
      aws_api_gateway_method.chat_save_post.id,
      aws_api_gateway_method.session_post.id,
      aws_api_gateway_method.session_get.id,
      aws_api_gateway_method.session_id_get.id,
      aws_api_gateway_method.session_id_put.id,
      aws_api_gateway_method.session_id_delete.id,
      aws_api_gateway_method.session_messages_get.id,
      aws_api_gateway_integration.diagram_generate_post.id,
      aws_api_gateway_integration.chat_history_get.id,
      aws_api_gateway_integration.chat_save_post.id,
      aws_api_gateway_integration.session_post.id,
      aws_api_gateway_integration.session_get.id,
      aws_api_gateway_integration.session_id_get.id,
      aws_api_gateway_integration.session_id_put.id,
      aws_api_gateway_integration.session_id_delete.id,
      aws_api_gateway_integration.session_messages_get.id,
      aws_api_gateway_method_response.diagram_generate_post_200.id,
      aws_api_gateway_method_response.chat_history_get_200.id,
      aws_api_gateway_method_response.chat_save_post_200.id,
      aws_api_gateway_method_response.session_post_200.id,
      aws_api_gateway_method_response.session_get_200.id,
      aws_api_gateway_method_response.session_id_get_200.id,
      aws_api_gateway_method_response.session_id_put_200.id,
      aws_api_gateway_method_response.session_id_delete_200.id,
      aws_api_gateway_method_response.session_messages_get_200.id,
      aws_api_gateway_integration_response.diagram_generate_post_200.id,
      aws_api_gateway_integration_response.chat_history_get_200.id,
      aws_api_gateway_integration_response.chat_save_post_200.id,
      aws_api_gateway_integration_response.session_post_200.id,
      aws_api_gateway_integration_response.session_get_200.id,
      aws_api_gateway_integration_response.session_id_get_200.id,
      aws_api_gateway_integration_response.session_id_put_200.id,
      aws_api_gateway_integration_response.session_id_delete_200.id,
      aws_api_gateway_integration_response.session_messages_get_200.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_method.diagram_generate_post,
    aws_api_gateway_method.chat_history_get,
    aws_api_gateway_method.chat_save_post,
    aws_api_gateway_method.session_post,
    aws_api_gateway_method.session_get,
    aws_api_gateway_method.session_id_get,
    aws_api_gateway_method.session_id_put,
    aws_api_gateway_method.session_id_delete,
    aws_api_gateway_method.session_messages_get,
    aws_api_gateway_integration.diagram_generate_post,
    aws_api_gateway_integration.chat_history_get,
    aws_api_gateway_integration.chat_save_post,
    aws_api_gateway_integration.session_post,
    aws_api_gateway_integration.session_get,
    aws_api_gateway_integration.session_id_get,
    aws_api_gateway_integration.session_id_put,
    aws_api_gateway_integration.session_id_delete,
    aws_api_gateway_integration.session_messages_get,
    aws_api_gateway_method.diagram_generate_options,
    aws_api_gateway_method.chat_history_options,
    aws_api_gateway_method.chat_save_options,
    aws_api_gateway_method.session_options,
    aws_api_gateway_method.session_id_options,
    aws_api_gateway_method.session_messages_options,
    aws_api_gateway_method_response.diagram_generate_post_200,
    aws_api_gateway_method_response.chat_history_get_200,
    aws_api_gateway_method_response.chat_save_post_200,
    aws_api_gateway_method_response.session_post_200,
    aws_api_gateway_method_response.session_get_200,
    aws_api_gateway_method_response.session_id_get_200,
    aws_api_gateway_method_response.session_id_put_200,
    aws_api_gateway_method_response.session_id_delete_200,
    aws_api_gateway_method_response.session_messages_get_200,
    aws_api_gateway_integration_response.diagram_generate_post_200,
    aws_api_gateway_integration_response.chat_history_get_200,
    aws_api_gateway_integration_response.chat_save_post_200,
    aws_api_gateway_integration_response.session_post_200,
    aws_api_gateway_integration_response.session_get_200,
    aws_api_gateway_integration_response.session_id_get_200,
    aws_api_gateway_integration_response.session_id_put_200,
    aws_api_gateway_integration_response.session_id_delete_200,
    aws_api_gateway_integration_response.session_messages_get_200,
  ]
}

# API Gateway stage
resource "aws_api_gateway_stage" "main" {
  deployment_id = aws_api_gateway_deployment.main.id
  rest_api_id   = aws_api_gateway_rest_api.main.id
  stage_name    = var.environment

  tags = {
    Name = "${var.project_name}-api-stage"
  }
}
