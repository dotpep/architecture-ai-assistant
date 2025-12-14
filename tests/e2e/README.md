# End-to-End Tests

End-to-end tests that verify complete user workflows through the entire application.

## Overview

E2E tests simulate real user interactions and verify that all components work together correctly.

## Test Structure

```
e2e/
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

## Test Scenarios

### 1. Chat Workflow
**File**: `specs/chat_workflow.spec.ts`

Tests the complete chat interaction flow:
1. User opens the application
2. User selects a diagram type
3. User enters a prompt
4. System sends request to API
5. API returns response
6. Frontend displays diagram
7. User can download diagram

### 2. Diagram Generation
**File**: `specs/diagram_generation.spec.ts`

Tests diagram generation for all supported types:
- Flowchart generation
- ERD generation
- Sequence diagram generation
- Class diagram generation
- State diagram generation
- Architecture diagram generation
- DFD generation

### 3. History Retrieval
**File**: `specs/history_retrieval.spec.ts`

Tests chat history functionality:
1. User opens application
2. Previous chats are loaded
3. User can view previous diagrams
4. User can re-render previous diagrams
5. Pagination works correctly

### 4. Error Handling
**File**: `specs/error_handling.spec.ts`

Tests error scenarios:
- Network errors
- API timeouts
- Invalid input
- Server errors
- CORS errors

## Running E2E Tests

### Prerequisites

```bash
# Install Playwright or Cypress
npm install --save-dev @playwright/test
# or
npm install --save-dev cypress
```

### Run All E2E Tests

```bash
# Using Playwright
npx playwright test tests/e2e/specs/

# Using Cypress
npx cypress run --spec "tests/e2e/specs/**/*.spec.ts"
```

### Run Specific Test

```bash
# Using Playwright
npx playwright test tests/e2e/specs/chat_workflow.spec.ts

# Using Cypress
npx cypress run --spec "tests/e2e/specs/chat_workflow.spec.ts"
```

### Run in Debug Mode

```bash
# Using Playwright
npx playwright test --debug

# Using Cypress
npx cypress open
```

## Example E2E Test

### Playwright Example

```typescript
import { test, expect } from '@playwright/test'

test.describe('Chat Workflow', () => {
  test('should complete full chat interaction', async ({ page }) => {
    // Navigate to application
    await page.goto('https://d1to0rasl28a6e.cloudfront.net')
    
    // Wait for page to load
    await page.waitForLoadState('networkidle')
    
    // Select diagram type
    await page.selectOption('select[name="diagramType"]', 'flowchart')
    
    // Enter prompt
    await page.fill('textarea[name="prompt"]', 'Create a login flowchart')
    
    // Submit
    await page.click('button:has-text("Generate")')
    
    // Wait for diagram to appear
    await page.waitForSelector('.diagram-container')
    
    // Verify diagram is displayed
    const diagram = await page.locator('.diagram-container')
    await expect(diagram).toBeVisible()
    
    // Verify download buttons appear
    const downloadBtn = await page.locator('button:has-text("Download")')
    await expect(downloadBtn).toBeVisible()
  })
})
```

### Cypress Example

```typescript
describe('Chat Workflow', () => {
  it('should complete full chat interaction', () => {
    // Navigate to application
    cy.visit('https://d1to0rasl28a6e.cloudfront.net')
    
    // Select diagram type
    cy.get('select[name="diagramType"]').select('flowchart')
    
    // Enter prompt
    cy.get('textarea[name="prompt"]').type('Create a login flowchart')
    
    // Submit
    cy.get('button:contains("Generate")').click()
    
    // Wait for diagram to appear
    cy.get('.diagram-container').should('be.visible')
    
    // Verify download buttons
    cy.get('button:contains("Download")').should('be.visible')
  })
})
```

## Page Objects

### PageObjects Helper

```typescript
// helpers/page_objects.ts

export class ChatPage {
  constructor(private page: Page) {}
  
  async navigateTo() {
    await this.page.goto('https://d1to0rasl28a6e.cloudfront.net')
  }
  
  async selectDiagramType(type: string) {
    await this.page.selectOption('select[name="diagramType"]', type)
  }
  
  async enterPrompt(prompt: string) {
    await this.page.fill('textarea[name="prompt"]', prompt)
  }
  
  async submitPrompt() {
    await this.page.click('button:has-text("Generate")')
  }
  
  async waitForDiagram() {
    await this.page.waitForSelector('.diagram-container')
  }
  
  async downloadDiagram(format: 'png' | 'md') {
    await this.page.click(`button:has-text("Download ${format.toUpperCase()}")`)
  }
}
```

## Test Data

### fixtures/test_data.json

```json
{
  "prompts": {
    "flowchart": "Create a simple login flowchart",
    "erdiagram": "Design a user database schema",
    "sequence": "Show a payment processing sequence"
  },
  "users": {
    "testUser": {
      "id": "test-user-1",
      "email": "test@example.com"
    }
  }
}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright
        run: npx playwright install
      
      - name: Run E2E tests
        run: npx playwright test tests/e2e/specs/
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: playwright-report
          path: playwright-report/
```

## Performance Considerations

- Tests should complete within 5 minutes
- Use parallel execution for faster results
- Implement proper waits instead of hard sleeps
- Clean up test data after execution

## Troubleshooting

### Tests Timing Out
- Increase timeout in configuration
- Check network connectivity
- Verify API Gateway is responding

### Flaky Tests
- Use explicit waits instead of implicit
- Implement retry logic
- Check for race conditions

### Browser Issues
- Update browser binaries: `npx playwright install`
- Check browser compatibility
- Verify headless mode settings

## Future Enhancements

- [ ] Visual regression testing
- [ ] Performance testing
- [ ] Accessibility testing
- [ ] Mobile device testing
- [ ] Multi-browser testing
- [ ] Load testing
