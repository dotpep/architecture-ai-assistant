# Testing Structure - Architecture AI Assistant

## Overview

The Architecture AI Assistant project now has a comprehensive, well-organized testing structure designed for scalability and future integration testing needs.

## Directory Structure

```
tests/
├── README.md                          # Main testing documentation
├── TESTING_GUIDE.md                   # Comprehensive testing guide
├── .env.example                       # Environment variables template
│
├── integration/                       # Integration Tests
│   ├── README.md                      # Integration test documentation
│   ├── payloads/                      # Test data and payloads
│   │   ├── dynamodb/
│   │   │   ├── put_operation.json     # DynamoDB PUT test
│   │   │   └── get_operation.json     # DynamoDB GET test
│   │   ├── s3/
│   │   │   ├── put_operation.json     # S3 PUT test
│   │   │   ├── get_operation.json     # S3 GET test
│   │   │   └── invalid_path.json      # IAM policy test
│   │   └── api/
│   │       ├── generate_diagram.json  # Generate diagram endpoint
│   │       ├── save_chat.json         # Save chat endpoint
│   │       └── get_history.json       # Get history endpoint
│   │
│   ├── lambda/                        # Lambda test functions
│   │   ├── test_dynamodb.py           # DynamoDB CRUD tests
│   │   └── test_s3.py                 # S3 operations tests
│   │
│   ├── results/                       # Test results and reports
│   │   └── integration_test_results.md # Latest test results
│   │
│   └── scripts/                       # Test execution scripts
│       ├── run_integration_tests.sh   # Main test runner
│       └── test_endpoints.sh          # API endpoint tests
│
├── unit/                              # Unit Tests (Future)
│   ├── README.md                      # Unit test documentation
│   ├── backend/
│   │   ├── test_prompt_builder.py
│   │   ├── test_mermaid_extractor.py
│   │   ├── test_mermaid_validator.py
│   │   └── test_aws_helpers.py
│   └── frontend/
│       ├── test_api_service.ts
│       ├── test_mermaid_parser.ts
│       └── test_components.test.tsx
│
└── e2e/                               # End-to-End Tests (Future)
    ├── README.md                      # E2E test documentation
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

## Test Categories

### 1. Integration Tests ✅ (Currently Implemented)

**Purpose**: Verify AWS services work together correctly

**Coverage**:
- Lambda → DynamoDB connectivity (CRUD operations)
- Lambda → S3 connectivity (file operations)
- API Gateway → Lambda routing
- CloudFront → S3 serving
- IAM policy enforcement
- CORS configuration

**Running**:
```bash
./tests/integration/scripts/run_integration_tests.sh
./tests/integration/scripts/test_endpoints.sh
```

**Results**: `tests/integration/results/integration_test_results.md`

### 2. Unit Tests 📋 (Planned)

**Purpose**: Test individual functions and components

**Coverage**:
- Backend: Prompt building, Mermaid extraction, validation
- Frontend: API service, Mermaid parsing, React components

**Running**:
```bash
pytest tests/unit/backend/
npm test -- tests/unit/frontend/
```

### 3. End-to-End Tests 📋 (Planned)

**Purpose**: Test complete user workflows

**Coverage**:
- Chat workflow
- Diagram generation (all types)
- History retrieval
- Error handling

**Running**:
```bash
npx playwright test tests/e2e/specs/
```

## Key Features

### 1. Organized Test Data
- Payloads organized by service (DynamoDB, S3, API)
- Easy to add new test cases
- Clear naming conventions

### 2. Reusable Test Functions
- Lambda test functions can be deployed and reused
- Test payloads can be used with AWS CLI
- Scripts are parameterized for flexibility

### 3. Comprehensive Documentation
- README files in each directory
- TESTING_GUIDE.md for overall guidance
- Inline comments in test files
- Example configurations

### 4. CI/CD Ready
- Scripts can be integrated into GitHub Actions
- Environment variables for configuration
- Test results stored for reporting
- Exit codes for automation

### 5. Scalable Structure
- Easy to add new test categories
- Clear separation of concerns
- Consistent naming and organization
- Future-proof design

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp tests/.env.example tests/.env

# Edit with your values
nano tests/.env
```

### 2. Run Integration Tests

```bash
# Make scripts executable
chmod +x tests/integration/scripts/*.sh

# Run all tests
./tests/integration/scripts/run_integration_tests.sh

# Run specific tests
./tests/integration/scripts/test_endpoints.sh
```

### 3. View Results

```bash
# Check integration test results
cat tests/integration/results/integration_test_results.md
```

## Adding New Tests

### Adding Integration Test

1. Create payload in `tests/integration/payloads/<service>/`
2. Add test function to `tests/integration/lambda/test_<service>.py`
3. Update test runner script
4. Document in README

### Adding Unit Test

1. Create test file in `tests/unit/<backend|frontend>/`
2. Follow naming convention: `test_<module>.py` or `test_<module>.ts`
3. Add to test runner configuration
4. Document in unit/README.md

### Adding E2E Test

1. Create spec file in `tests/e2e/specs/`
2. Use page objects from `tests/e2e/helpers/`
3. Add test data to `tests/e2e/fixtures/`
4. Document in e2e/README.md

## Test Results

### Integration Tests
- **Status**: ✅ All Passing
- **Last Run**: 2024-12-14
- **Results**: `tests/integration/results/integration_test_results.md`

### Unit Tests
- **Status**: 📋 Planned
- **Coverage Goal**: 80% (backend), 75% (frontend)

### E2E Tests
- **Status**: 📋 Planned
- **Coverage**: All user workflows

## Best Practices

1. **Test Isolation** - Each test is independent
2. **Clear Naming** - Test names describe what they test
3. **Arrange-Act-Assert** - Follow AAA pattern
4. **Error Handling** - Test both success and failure
5. **Performance** - Keep tests fast
6. **Documentation** - Document test purpose and usage

## Future Enhancements

- [ ] Automated test scheduling
- [ ] Performance benchmarking
- [ ] Load testing
- [ ] Chaos engineering tests
- [ ] Security scanning
- [ ] Cost analysis tests
- [ ] Visual regression testing
- [ ] Accessibility testing
- [ ] Multi-region testing

## Resources

- **Main Guide**: `tests/TESTING_GUIDE.md`
- **Integration Tests**: `tests/integration/README.md`
- **Unit Tests**: `tests/unit/README.md`
- **E2E Tests**: `tests/e2e/README.md`
- **Test Results**: `tests/integration/results/integration_test_results.md`

## Support

For questions or issues:
1. Check relevant README in tests directory
2. Review TESTING_GUIDE.md
3. Check test results for error details
4. Review CloudWatch logs for Lambda execution

---

**Created**: 2024-12-14
**Last Updated**: 2024-12-14
**Status**: Integration tests implemented and passing ✅
