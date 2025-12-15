# Playwright E2E Tests

This directory contains Playwright end-to-end tests for the Architecture AI Assistant, including comprehensive tests for the new session management features.

## Test Structure

```
playwright/
├── README.md
├── package.json
├── playwright.config.ts
├── node_modules/
└── tests/
    ├── playwright_app_test.spec.ts          # Original comprehensive tests
    └── session_management_tests.spec.ts     # Session management specific tests
```

## Test Files

### playwright_app_test.spec.ts
Comprehensive tests covering all original requirements:
- Chat interface functionality
- Diagram generation and rendering
- File storage and downloads
- Chat history persistence
- API endpoints
- Frontend hosting
- Error handling

### session_management_tests.spec.ts
Tests for new session management features:
- Session creation and navigation
- Session title generation
- Session-based message organization
- Session API endpoints
- Session persistence across page reloads
- Error handling for session operations

## Running Tests

### Prerequisites
```bash
cd tests/e2e/playwright
npm install
npx playwright install
```

### Run All Tests
```bash
npx playwright test
```

### Run Specific Test File
```bash
npx playwright test tests/session_management_tests.spec.ts
```

### Run Tests in Headed Mode (with browser UI)
```bash
npx playwright test --headed
```

### Run Tests with Debug Mode
```bash
npx playwright test --debug
```

### Generate Test Report
```bash
npx playwright show-report
```

## Test Configuration

The `playwright.config.ts` file configures:
- Multiple browser testing (Chrome, Firefox, Safari, Edge)
- Mobile device testing
- Screenshot and video capture on failures
- Test timeouts and retries
- Reporting formats (HTML, JSON, JUnit)

## Test Coverage

### Session Management Features
- ✅ Session creation via "New Chat" button
- ✅ Session title generation from first message
- ✅ Session list display with date grouping
- ✅ Session selection and message loading
- ✅ Session highlighting in sidebar
- ✅ Session API endpoints (CRUD operations)
- ✅ Session workflow across multiple messages
- ✅ Session persistence across page reloads
- ✅ Error handling for invalid sessions

### Original Features
- ✅ Chat interface components
- ✅ Diagram generation for all types
- ✅ Mermaid code validation and rendering
- ✅ File downloads (PNG/Markdown)
- ✅ Chat history persistence
- ✅ API endpoint functionality
- ✅ Frontend hosting via CloudFront
- ✅ CORS configuration
- ✅ Error handling and recovery

## Browser Support

Tests run on:
- Desktop: Chrome, Firefox, Safari, Edge
- Mobile: Chrome (Pixel 5), Safari (iPhone 12)

## CI/CD Integration

The tests are configured for CI/CD with:
- Retry logic for flaky tests
- Parallel execution control
- Multiple output formats
- Artifact collection (screenshots, videos, traces)

## Troubleshooting

### Common Issues

1. **Tests timing out**
   - Increase timeout in playwright.config.ts
   - Check network connectivity to CloudFront/API Gateway

2. **Element not found errors**
   - Verify frontend is deployed and accessible
   - Check if UI components have expected data-testid attributes

3. **API endpoint failures**
   - Verify API Gateway deployment
   - Check Lambda function status
   - Verify CORS configuration

### Debug Mode

Use debug mode to step through tests:
```bash
npx playwright test --debug tests/session_management_tests.spec.ts
```

### Screenshots and Videos

Failed tests automatically capture:
- Screenshots at point of failure
- Video recordings of test execution
- Network traces for debugging

Files are saved to `test-results/` directory.

## Performance Considerations

- Tests use `waitUntil: 'networkidle'` for reliable page loads
- Timeouts are configured for slow API responses
- Parallel execution is limited on CI to avoid resource conflicts

## Future Enhancements

- [ ] Visual regression testing
- [ ] Performance benchmarking
- [ ] Accessibility testing with axe-core
- [ ] Cross-browser compatibility matrix
- [ ] Load testing scenarios