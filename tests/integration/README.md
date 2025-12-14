# Integration Tests

Comprehensive integration tests for the Architecture AI Assistant project.

## Overview

This directory contains all integration tests that verify the interaction between different AWS services and components:

- Lambda functions ↔ DynamoDB
- Lambda functions ↔ S3
- API Gateway ↔ Lambda functions
- CloudFront ↔ S3 (Frontend serving)
- Frontend ↔ API Gateway

## Test Payloads

### DynamoDB Payloads

Located in `payloads/dynamodb/`:

- `put_operation.json` - Create/update item in DynamoDB
- `get_operation.json` - Retrieve item from DynamoDB
- `query_operation.json` - Query items with pagination

### S3 Payloads

Located in `payloads/s3/`:

- `put_operation.json` - Upload file to S3 (diagrams/ prefix)
- `get_operation.json` - Retrieve file from S3
- `invalid_path.json` - Test IAM policy restrictions

### API Gateway Payloads

Located in `payloads/api/`:

- `generate_diagram.json` - POST /api/diagram/generate
- `save_chat.json` - POST /api/chat/save
- `get_history.json` - GET /api/chat/history

## Lambda Test Functions

### test_dynamodb.py

Tests DynamoDB CRUD operations:

```python
# PUT operation
aws lambda invoke --function-name architecture-ai-assistant-chat-crud-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://payloads/dynamodb/put_operation.json \
  response.json

# GET operation
aws lambda invoke --function-name architecture-ai-assistant-chat-crud-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://payloads/dynamodb/get_operation.json \
  response.json
```

### test_s3.py

Tests S3 operations:

```python
# PUT operation (correct path)
aws lambda invoke --function-name architecture-ai-assistant-generate-diagram-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://payloads/s3/put_operation.json \
  response.json

# GET operation
aws lambda invoke --function-name architecture-ai-assistant-generate-diagram-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://payloads/s3/get_operation.json \
  response.json
```

## Test Execution Scripts

### run_integration_tests.sh

Main test runner that executes all integration tests:

```bash
./scripts/run_integration_tests.sh
```

Runs:
1. DynamoDB connectivity tests
2. S3 connectivity tests
3. API Gateway endpoint tests
4. Frontend accessibility tests
5. IAM policy validation tests

### test_endpoints.sh

Tests API Gateway endpoints directly:

```bash
./scripts/test_endpoints.sh
```

Tests:
1. POST /api/diagram/generate
2. POST /api/chat/save
3. GET /api/chat/history
4. CORS headers

## Test Results

Results are stored in `results/integration_test_results.md` with:

- Test execution timestamp
- Pass/fail status for each test
- Error messages and details
- Performance metrics
- IAM policy validation results

## Configuration

### Environment Variables

Create a `.env` file in this directory:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# Resource Names
DYNAMODB_TABLE_NAME=architecture-ai-assistant-chat_history-dev
S3_BUCKET_NAME=architecture-ai-assistant-bucket-dev
LAMBDA_CHAT_CRUD=architecture-ai-assistant-chat-crud-dev
LAMBDA_GENERATE_DIAGRAM=architecture-ai-assistant-generate-diagram-dev
LAMBDA_GET_HISTORY=architecture-ai-assistant-get-history-dev

# API Configuration
API_GATEWAY_URL=https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev
CLOUDFRONT_URL=https://d1to0rasl28a6e.cloudfront.net

# Test Configuration
TEST_TIMEOUT=30
RETRY_ATTEMPTS=3
```

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Clean up test data after execution
- Use unique identifiers for test data

### 2. Error Handling
- Capture detailed error messages
- Log AWS API responses
- Include CloudWatch log links in results

### 3. Performance
- Measure Lambda execution time
- Track API response times
- Monitor S3 and DynamoDB latency

### 4. Security
- Never commit AWS credentials
- Use IAM roles for test execution
- Validate IAM policy restrictions

### 5. Documentation
- Document each test's purpose
- Include expected vs actual results
- Provide troubleshooting guides

## Common Issues and Solutions

### Issue: AccessDenied on S3 PutObject

**Cause**: Lambda trying to write to wrong S3 prefix

**Solution**: Ensure file key starts with `diagrams/`

```json
{
  "body": "{\"operation\": \"PUT\", \"fileKey\": \"diagrams/test-file.txt\", \"content\": \"test\"}"
}
```

### Issue: DynamoDB Item Not Found

**Cause**: Incorrect chatId or timestamp

**Solution**: Use exact values from PUT operation

```json
{
  "body": "{\"operation\": \"GET\", \"chatId\": \"integration-test-1\", \"timestamp\": 1734217200}"
}
```

### Issue: CORS Errors from Frontend

**Cause**: CloudFront cache not invalidated

**Solution**: Invalidate CloudFront cache

```bash
aws cloudfront create-invalidation --distribution-id E169G4IKZZ4BI0 --paths "/*"
```

## Future Enhancements

- [ ] Automated test scheduling
- [ ] Performance regression detection
- [ ] Cost tracking per test
- [ ] Multi-region testing
- [ ] Chaos engineering tests
- [ ] Security compliance tests
