# Quick Reference - Testing Commands

## Integration Tests

### Run All Tests
```bash
./tests/integration/scripts/run_integration_tests.sh
```

### Run API Endpoint Tests
```bash
./tests/integration/scripts/test_endpoints.sh
```

### Test DynamoDB PUT
```bash
aws lambda invoke --function-name architecture-ai-assistant-chat-crud-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://tests/integration/payloads/dynamodb/put_operation.json \
  response.json
```

### Test DynamoDB GET
```bash
aws lambda invoke --function-name architecture-ai-assistant-chat-crud-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://tests/integration/payloads/dynamodb/get_operation.json \
  response.json
```

### Test S3 PUT
```bash
aws lambda invoke --function-name architecture-ai-assistant-generate-diagram-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://tests/integration/payloads/s3/put_operation.json \
  response.json
```

### Test S3 GET
```bash
aws lambda invoke --function-name architecture-ai-assistant-generate-diagram-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://tests/integration/payloads/s3/get_operation.json \
  response.json
```

### Test IAM Policy (Should Fail)
```bash
aws lambda invoke --function-name architecture-ai-assistant-generate-diagram-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://tests/integration/payloads/s3/invalid_path.json \
  response.json
```

## Unit Tests (Future)

### Backend Tests
```bash
pytest tests/unit/backend/
pytest tests/unit/backend/test_prompt_builder.py
pytest tests/unit/backend/ --cov=src/backend
```

### Frontend Tests
```bash
npm test -- tests/unit/frontend/
npm test -- tests/unit/frontend/test_api_service.ts
npm test -- tests/unit/frontend/ --coverage
```

## E2E Tests (Future)

### Run All E2E Tests
```bash
npx playwright test tests/e2e/specs/
```

### Run Specific Test
```bash
npx playwright test tests/e2e/specs/chat_workflow.spec.ts
```

### Debug Mode
```bash
npx playwright test --debug
```

### UI Mode
```bash
npx playwright test --ui
```

## View Results

### Integration Test Results
```bash
cat tests/integration/results/integration_test_results.md
```

### Check Response
```bash
cat response.json
```

## Configuration

### Setup Environment
```bash
cp tests/.env.example tests/.env
nano tests/.env
```

### Make Scripts Executable
```bash
chmod +x tests/integration/scripts/*.sh
```

## Documentation

### Main Guides
- `tests/README.md` - Overview
- `tests/TESTING_GUIDE.md` - Comprehensive guide
- `TESTING_STRUCTURE.md` - Structure overview
- `INTEGRATION_TESTS_SUMMARY.md` - Summary

### Specific Documentation
- `tests/integration/README.md` - Integration tests
- `tests/unit/README.md` - Unit tests
- `tests/e2e/README.md` - E2E tests

## Test Payloads

### DynamoDB
- `tests/integration/payloads/dynamodb/put_operation.json`
- `tests/integration/payloads/dynamodb/get_operation.json`

### S3
- `tests/integration/payloads/s3/put_operation.json`
- `tests/integration/payloads/s3/get_operation.json`
- `tests/integration/payloads/s3/invalid_path.json`

### API
- `tests/integration/payloads/api/generate_diagram.json`
- `tests/integration/payloads/api/save_chat.json`
- `tests/integration/payloads/api/get_history.json`

## Lambda Functions

### Test Functions
- `tests/integration/lambda/test_dynamodb.py`
- `tests/integration/lambda/test_s3.py`

### Deployed Functions
- `architecture-ai-assistant-chat-crud-dev`
- `architecture-ai-assistant-generate-diagram-dev`
- `architecture-ai-assistant-get-history-dev`

## Common Issues

### AccessDenied on S3
**Solution**: Use `diagrams/` prefix in file key

### DynamoDB Item Not Found
**Solution**: Use exact chatId and timestamp from PUT operation

### CORS Errors
**Solution**: Invalidate CloudFront cache
```bash
aws cloudfront create-invalidation --distribution-id E169G4IKZZ4BI0 --paths "/*"
```

### Tests Timing Out
**Solution**: Increase timeout in configuration

### Browser Not Found (E2E)
**Solution**: Install browsers
```bash
npx playwright install
```

## AWS Resources

- **API Gateway**: https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev
- **CloudFront**: https://d1to0rasl28a6e.cloudfront.net
- **DynamoDB Table**: architecture-ai-assistant-chat_history-dev
- **S3 Bucket**: architecture-ai-assistant-bucket-dev
- **Region**: us-east-1

## Test Status

✅ **Integration Tests**: All Passing
📋 **Unit Tests**: Planned
📋 **E2E Tests**: Planned

## Quick Links

- [Main Testing Guide](tests/TESTING_GUIDE.md)
- [Integration Tests](tests/integration/README.md)
- [Test Results](tests/integration/results/integration_test_results.md)
- [Structure Overview](TESTING_STRUCTURE.md)
