# Testing Guide

Comprehensive guide for testing the Architecture AI Assistant project.

## Overview

This project uses a three-tier testing strategy:

1. **Unit Tests** - Test individual functions and components
2. **Integration Tests** - Test interactions between services
3. **End-to-End Tests** - Test complete user workflows

## Quick Start

### Run All Tests

```bash
# Integration tests
./tests/integration/scripts/run_integration_tests.sh

# Unit tests (backend)
pytest tests/unit/backend/

# Unit tests (frontend)
npm test -- tests/unit/frontend/

# E2E tests
npx playwright test tests/e2e/specs/
```

### Run Specific Test Suite

```bash
# DynamoDB integration tests
aws lambda invoke --function-name architecture-ai-assistant-chat-crud-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://tests/integration/payloads/dynamodb/put_operation.json \
  response.json

# S3 integration tests
aws lambda invoke --function-name architecture-ai-assistant-generate-diagram-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://tests/integration/payloads/s3/put_operation.json \
  response.json

# API Gateway tests
./tests/integration/scripts/test_endpoints.sh
```

## Test Organization

```
tests/
├── README.md                          # Main testing documentation
├── TESTING_GUIDE.md                   # This file
├── integration/                       # Integration tests
│   ├── README.md
│   ├── payloads/                      # Test data
│   │   ├── dynamodb/
│   │   ├── s3/
│   │   └── api/
│   ├── lambda/                        # Lambda test functions
│   │   ├── test_dynamodb.py
│   │   └── test_s3.py
│   ├── results/                       # Test results
│   │   └── integration_test_results.md
│   └── scripts/                       # Test runners
│       ├── run_integration_tests.sh
│       └── test_endpoints.sh
├── unit/                              # Unit tests
│   ├── README.md
│   ├── backend/
│   │   ├── test_prompt_builder.py
│   │   ├── test_mermaid_extractor.py
│   │   ├── test_mermaid_validator.py
│   │   └── test_aws_helpers.py
│   └── frontend/
│       ├── test_api_service.ts
│       ├── test_mermaid_parser.ts
│       └── test_components.test.tsx
└── e2e/                               # End-to-end tests
    ├── README.md
    ├── fixtures/
    │   ├── test_data.json
    │   └── mock_responses.json
    ├── specs/
    │   ├── chat_workflow.spec.ts
    │   ├── diagram_generation.spec.ts
    │   ├── history_retrieval.spec.ts
    │   └── error_handling.spec.ts
    └── helpers/
        ├── page_objects.ts
        └── test_utils.ts
```

## Integration Tests

### Purpose
Verify that different AWS services work together correctly:
- Lambda ↔ DynamoDB
- Lambda ↔ S3
- API Gateway ↔ Lambda
- CloudFront ↔ S3
- Frontend ↔ API Gateway

### Running Integration Tests

```bash
# Run all integration tests
./tests/integration/scripts/run_integration_tests.sh

# Run specific test
aws lambda invoke --function-name architecture-ai-assistant-chat-crud-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://tests/integration/payloads/dynamodb/put_operation.json \
  response.json
```

### Test Coverage

- ✅ DynamoDB PUT/GET operations
- ✅ S3 PUT/GET operations
- ✅ IAM policy restrictions
- ✅ CloudFront distribution
- ✅ API Gateway endpoints
- ✅ CORS configuration

### Expected Results

All integration tests should pass with status code 200 (or expected error codes).

See `tests/integration/results/integration_test_results.md` for detailed results.

## Unit Tests

### Purpose
Test individual functions and components in isolation.

### Backend Unit Tests

```bash
# Run all backend tests
pytest tests/unit/backend/

# Run specific test file
pytest tests/unit/backend/test_prompt_builder.py

# Run with coverage
pytest tests/unit/backend/ --cov=src/backend --cov-report=html
```

**Test Files:**
- `test_prompt_builder.py` - LLM prompt construction
- `test_mermaid_extractor.py` - Mermaid code extraction
- `test_mermaid_validator.py` - Mermaid syntax validation
- `test_aws_helpers.py` - AWS service helpers

### Frontend Unit Tests

```bash
# Run all frontend tests
npm test -- tests/unit/frontend/

# Run specific test file
npm test -- tests/unit/frontend/test_api_service.ts

# Run with coverage
npm test -- tests/unit/frontend/ --coverage
```

**Test Files:**
- `test_api_service.ts` - API service functions
- `test_mermaid_parser.ts` - Mermaid parsing
- `test_components.test.tsx` - React components

### Coverage Goals

- Backend: Minimum 80%
- Frontend: Minimum 75%
- Critical paths: 100%

## End-to-End Tests

### Purpose
Test complete user workflows through the entire application.

### Running E2E Tests

```bash
# Run all E2E tests
npx playwright test tests/e2e/specs/

# Run specific test
npx playwright test tests/e2e/specs/chat_workflow.spec.ts

# Run in debug mode
npx playwright test --debug

# Run with UI mode
npx playwright test --ui
```

### Test Scenarios

1. **Chat Workflow** - Complete chat interaction
2. **Diagram Generation** - All diagram types
3. **History Retrieval** - Chat history and pagination
4. **Error Handling** - Error scenarios

### Expected Results

All E2E tests should complete successfully with user workflows functioning correctly.

## Test Data

### Integration Test Payloads

Located in `tests/integration/payloads/`:

**DynamoDB:**
- `put_operation.json` - Create/update item
- `get_operation.json` - Retrieve item

**S3:**
- `put_operation.json` - Upload file
- `get_operation.json` - Retrieve file
- `invalid_path.json` - Test IAM restrictions

**API:**
- `generate_diagram.json` - Generate diagram request
- `save_chat.json` - Save chat request
- `get_history.json` - Get history request

### Using Test Data

```bash
# Use test payload with Lambda
aws lambda invoke --function-name <function-name> \
  --cli-binary-format raw-in-base64-out \
  --payload file://tests/integration/payloads/<service>/<operation>.json \
  response.json
```

## Configuration

### Environment Variables

Create `.env` file in tests directory:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# Resource Names
DYNAMODB_TABLE_NAME=architecture-ai-assistant-chat_history-dev
S3_BUCKET_NAME=architecture-ai-assistant-bucket-dev
LAMBDA_CHAT_CRUD=architecture-ai-assistant-chat-crud-dev
LAMBDA_GENERATE_DIAGRAM=architecture-ai-assistant-generate-diagram-dev

# API Configuration
API_GATEWAY_URL=https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev
CLOUDFRONT_URL=https://d1to0rasl28a6e.cloudfront.net

# Test Configuration
TEST_TIMEOUT=30
RETRY_ATTEMPTS=3
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: ./tests/integration/scripts/run_integration_tests.sh

  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm ci
      - run: pytest tests/unit/backend/
      - run: npm test -- tests/unit/frontend/

  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm ci
      - run: npx playwright install
      - run: npx playwright test tests/e2e/specs/
```

## Troubleshooting

### Integration Tests

**Issue**: AccessDenied on S3 operations
- **Solution**: Ensure file key starts with `diagrams/`

**Issue**: DynamoDB item not found
- **Solution**: Use exact PK and SK values from PUT operation (session-based data model)

**Issue**: CORS errors
- **Solution**: Invalidate CloudFront cache

### Unit Tests

**Issue**: Import errors
- **Solution**: Ensure Python path includes src directory

**Issue**: Module not found
- **Solution**: Install dependencies: `pip install -r requirements.txt`

### E2E Tests

**Issue**: Tests timing out
- **Solution**: Increase timeout in playwright.config.ts

**Issue**: Flaky tests
- **Solution**: Use explicit waits instead of hard sleeps

**Issue**: Browser not found
- **Solution**: Run `npx playwright install`

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Clean up test data after execution
- Use unique identifiers for test data

### 2. Clear Naming
- Test names should describe what is being tested
- Use descriptive variable names
- Include expected behavior in test name

### 3. Arrange-Act-Assert
```python
# Arrange - Set up test data
chat_id = "test-123"
timestamp = 1234567890

# Act - Perform the action
response = table.get_item(Key={'chatId': chat_id, 'timestamp': timestamp})

# Assert - Verify the result
assert response['Item']['chatId'] == chat_id
```

### 4. Error Handling
- Test both success and failure cases
- Verify error messages are helpful
- Test edge cases and boundary conditions

### 5. Performance
- Keep tests fast (< 5 seconds each)
- Use parallel execution when possible
- Avoid unnecessary waits

## Continuous Testing

### Automated Test Execution

Tests can be run automatically on:
- Every commit (pre-commit hooks)
- Every push (CI/CD pipeline)
- On schedule (nightly tests)
- Before deployment

### Test Reports

Test results are stored in:
- `tests/integration/results/` - Integration test results
- `coverage/` - Code coverage reports
- `playwright-report/` - E2E test reports

## Future Enhancements

- [ ] Performance benchmarking tests
- [ ] Load testing with concurrent requests
- [ ] Chaos engineering tests
- [ ] Security scanning and penetration tests
- [ ] Cost analysis and optimization tests
- [ ] Visual regression testing
- [ ] Accessibility testing
- [ ] Multi-region testing

## Resources

- [AWS Lambda Testing](https://docs.aws.amazon.com/lambda/latest/dg/testing-functions.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Cypress Documentation](https://docs.cypress.io/)

## Support

For issues or questions about testing:
1. Check the troubleshooting section
2. Review test documentation in each directory
3. Check CloudWatch logs for Lambda execution details
4. Review test results in `tests/integration/results/`
