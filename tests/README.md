# Integration Tests

This directory contains integration tests for the Architecture AI Assistant project.

## Structure

```
tests/
├── README.md                          # This file
├── integration/                       # Integration test suite
│   ├── README.md                      # Integration test documentation
│   ├── payloads/                      # Test payload files
│   │   ├── dynamodb/                  # DynamoDB test payloads
│   │   ├── s3/                        # S3 test payloads
│   │   └── api/                       # API Gateway test payloads
│   ├── results/                       # Test results and reports
│   │   └── integration_test_results.md
│   ├── lambda/                        # Lambda test functions
│   │   ├── test_dynamodb.py
│   │   └── test_s3.py
│   └── scripts/                       # Test execution scripts
│       ├── run_integration_tests.sh
│       └── test_endpoints.sh
├── unit/                              # Unit tests (future)
│   └── README.md
└── e2e/                               # End-to-end tests (future)
    └── README.md
```

## Running Integration Tests

### Prerequisites
- AWS CLI configured with appropriate credentials
- Access to deployed AWS resources
- CloudFront URL and API Gateway URL from Terraform outputs

### Quick Start

```bash
# Run all integration tests
./tests/integration/scripts/run_integration_tests.sh

# Run specific test suite
./tests/integration/scripts/test_endpoints.sh
```

## Test Categories

### 1. Lambda → DynamoDB Tests
- **Location**: `tests/integration/lambda/test_dynamodb.py`
- **Payloads**: `tests/integration/payloads/dynamodb/`
- **Tests**:
  - PUT operation (create/update items)
  - GET operation (retrieve items)
  - Query operations (pagination)

### 2. Lambda → S3 Tests
- **Location**: `tests/integration/lambda/test_s3.py`
- **Payloads**: `tests/integration/payloads/s3/`
- **Tests**:
  - PUT operation (upload files)
  - GET operation (retrieve files)
  - Path restrictions (IAM policy validation)

### 3. API Gateway Tests
- **Location**: `tests/integration/payloads/api/`
- **Tests**:
  - POST /api/diagram/generate
  - POST /api/chat/save
  - GET /api/chat/history
  - CORS configuration

### 4. Frontend Tests
- **Location**: `tests/integration/scripts/test_endpoints.sh`
- **Tests**:
  - CloudFront distribution serving frontend
  - API Gateway connectivity from frontend
  - Error handling and retry logic

## Test Results

Latest test results are stored in `tests/integration/results/integration_test_results.md`

## Adding New Tests

1. Create test payload in appropriate subdirectory under `tests/integration/payloads/`
2. Add test function to corresponding Lambda test file
3. Update test execution script to include new test
4. Document test in this README

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Integration Tests
  run: ./tests/integration/scripts/run_integration_tests.sh
```

## Troubleshooting

### AccessDenied Errors
- Verify IAM policies allow the operation
- Check S3 path restrictions (diagrams/ prefix for generate_diagram Lambda)
- Ensure Lambda execution role has required permissions

### Timeout Errors
- Increase Lambda timeout in Terraform configuration
- Check CloudWatch logs for Lambda execution details
- Verify network connectivity to AWS services

### CORS Errors
- Verify API Gateway CORS configuration
- Check CloudFront cache invalidation
- Clear browser cache and retry

## Future Enhancements

- [ ] Automated test execution on deployment
- [ ] Performance benchmarking tests
- [ ] Load testing with concurrent requests
- [ ] Chaos engineering tests
- [ ] Security scanning and penetration tests
- [ ] Cost analysis and optimization tests
