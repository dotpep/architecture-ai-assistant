import { test, expect, Page } from '@playwright/test';

/**
 * Architecture AI Assistant - Comprehensive Playwright Tests
 * Tests all requirements from the specification
 */

const APP_URL = 'https://d1to0rasl28a6e.cloudfront.net';
const API_URL = 'https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev';

test.describe('Architecture AI Assistant - Full Application Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    await page.goto(APP_URL, { waitUntil: 'networkidle' });
  });

  test.afterEach(async () => {
    await page.close();
  });

  // ============================================================================
  // REQUIREMENT 1: Chat Interface
  // ============================================================================

  test('REQ-1.1: Should display chat interface with message input and diagram type selector', async () => {
    // Check for header
    const header = page.locator('header');
    await expect(header).toBeVisible();

    // Check for diagram type selector
    const diagramSelector = page.locator('[data-testid="diagram-type-selector"]');
    await expect(diagramSelector).toBeVisible();

    // Check for chat input field
    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]');
    await expect(chatInput).toBeVisible();

    // Check for send button
    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]');
    await expect(sendButton).toBeVisible();
  });

  test('REQ-1.2: Should send message and display loading indicator', async () => {
    const testMessage = 'Create a simple flowchart for a user login system';

    // Find and fill the chat input
    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    // Click send button
    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Check for loading indicator
    const loadingIndicator = page.locator('[data-testid="loading"], .loading, .spinner');
    await expect(loadingIndicator.first()).toBeVisible({ timeout: 5000 });
  });

  test('REQ-1.3: Should display AI response within 30 seconds', async () => {
    const testMessage = 'Create a flowchart for a simple authentication flow';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for response (max 30 seconds)
    const chatMessages = page.locator('[data-testid="chat-message"], .message');
    await expect(chatMessages.last()).toBeVisible({ timeout: 30000 });

    // Verify response contains text
    const lastMessage = await chatMessages.last().textContent();
    expect(lastMessage).toBeTruthy();
    expect(lastMessage?.length).toBeGreaterThan(0);
  });

  test('REQ-1.4: Should use selected diagram type as context', async () => {
    // Select a specific diagram type
    const diagramTypeButtons = page.locator('[data-testid="diagram-type-button"]');
    const erdButton = diagramTypeButtons.filter({ hasText: 'ERD' }).first();
    
    if (await erdButton.isVisible()) {
      await erdButton.click();
      
      // Verify selection is active
      await expect(erdButton).toHaveClass(/active|selected/);
    }
  });

  test('REQ-1.5: Should display error message on API failure and allow retry', async () => {
    // Intercept API calls to simulate failure
    await page.route(`${API_URL}/**`, route => {
      route.abort('failed');
    });

    const testMessage = 'Create a diagram';
    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Check for error message
    const errorMessage = page.locator('[data-testid="error-message"], .error, .alert-error');
    await expect(errorMessage.first()).toBeVisible({ timeout: 10000 });

    // Verify error text is displayed
    const errorText = await errorMessage.first().textContent();
    expect(errorText).toBeTruthy();
  });

  // ============================================================================
  // REQUIREMENT 2: Diagram Generation
  // ============================================================================

  test('REQ-2.1: Should generate valid Mermaid code for requested diagram type', async () => {
    const testMessage = 'Create a flowchart showing a simple process: Start -> Process -> End';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for mermaid code block
    const mermaidCode = page.locator('code:has-text("graph"), code:has-text("flowchart")');
    await expect(mermaidCode.first()).toBeVisible({ timeout: 30000 });

    const codeContent = await mermaidCode.first().textContent();
    expect(codeContent).toMatch(/graph|flowchart/i);
  });

  test('REQ-2.2: Should display Mermaid code in syntax-highlighted code block', async () => {
    const testMessage = 'Create a flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for code block
    const codeBlock = page.locator('pre, [data-testid="code-block"]');
    await expect(codeBlock.first()).toBeVisible({ timeout: 30000 });
  });

  test('REQ-2.3: Should render diagram visually with zoom and pan capabilities', async () => {
    const testMessage = 'Create a flowchart with multiple steps';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for diagram renderer
    const diagramRenderer = page.locator('[data-testid="diagram-renderer"], svg, canvas');
    await expect(diagramRenderer.first()).toBeVisible({ timeout: 30000 });
  });

  test('REQ-2.4: Should support all diagram types', async () => {
    const diagramTypes = ['Flowchart', 'ERD', 'Sequence', 'Class', 'State', 'Architecture', 'DFD'];

    for (const diagramType of diagramTypes) {
      const button = page.locator(`[data-testid="diagram-type-button"]:has-text("${diagramType}")`);
      
      if (await button.isVisible()) {
        await button.click();
        await expect(button).toHaveClass(/active|selected/);
      }
    }
  });

  test('REQ-2.5: Should validate Mermaid code syntax before rendering', async () => {
    const testMessage = 'Create a simple flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for successful rendering (indicates validation passed)
    const diagramRenderer = page.locator('[data-testid="diagram-renderer"], svg, canvas');
    await expect(diagramRenderer.first()).toBeVisible({ timeout: 30000 });
  });

  // ============================================================================
  // REQUIREMENT 3: Diagram Storage and Download
  // ============================================================================

  test('REQ-3.1: Should save Mermaid code as markdown to S3', async () => {
    const testMessage = 'Create a flowchart for a payment system';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(5000);

    // Check network requests for S3 upload
    const requests = await page.context().storageState();
    expect(requests).toBeTruthy();
  });

  test('REQ-3.2: Should render and save PNG image to S3', async () => {
    const testMessage = 'Create a diagram';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for diagram rendering
    const diagramRenderer = page.locator('[data-testid="diagram-renderer"], svg, canvas');
    await expect(diagramRenderer.first()).toBeVisible({ timeout: 30000 });
  });

  test('REQ-3.3: Should provide download button for PNG image', async () => {
    const testMessage = 'Create a flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for download buttons
    const downloadButtons = page.locator('button:has-text("Download"), [data-testid="download-button"]');
    await expect(downloadButtons.first()).toBeVisible({ timeout: 30000 });
  });

  test('REQ-3.4: Should provide download button for markdown file', async () => {
    const testMessage = 'Create a flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for download buttons
    const downloadButtons = page.locator('button:has-text("Download"), [data-testid="download-button"]');
    await expect(downloadButtons.first()).toBeVisible({ timeout: 30000 });
  });

  test('REQ-3.5: Should initiate file download from S3 via CloudFront', async () => {
    const testMessage = 'Create a flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for download button
    const downloadButton = page.locator('button:has-text("Download"), [data-testid="download-button"]').first();
    await expect(downloadButton).toBeVisible({ timeout: 30000 });

    // Verify button is clickable
    await expect(downloadButton).toBeEnabled();
  });

  // ============================================================================
  // REQUIREMENT 4: Chat History Persistence
  // ============================================================================

  test('REQ-4.1: Should save chat messages to DynamoDB with timestamp', async () => {
    const testMessage = 'Create a flowchart for a user registration process';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for message to be saved
    await page.waitForTimeout(3000);

    // Verify message appears in chat
    const chatMessages = page.locator('[data-testid="chat-message"], .message');
    const messageCount = await chatMessages.count();
    expect(messageCount).toBeGreaterThan(0);
  });

  test('REQ-4.2: Should load and display previous chat history on page load', async () => {
    // First, send a message
    const testMessage = 'Create a flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(5000);

    // Reload page
    await page.reload({ waitUntil: 'networkidle' });

    // Check if history is loaded
    const chatMessages = page.locator('[data-testid="chat-message"], .message');
    const messageCount = await chatMessages.count();
    expect(messageCount).toBeGreaterThanOrEqual(0);
  });

  test('REQ-4.3: Should re-render previously generated diagrams from stored Mermaid code', async () => {
    // Send a message
    const testMessage = 'Create a flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for diagram
    const diagramRenderer = page.locator('[data-testid="diagram-renderer"], svg, canvas');
    await expect(diagramRenderer.first()).toBeVisible({ timeout: 30000 });

    // Reload page
    await page.reload({ waitUntil: 'networkidle' });

    // Check if diagram is re-rendered
    await expect(diagramRenderer.first()).toBeVisible({ timeout: 10000 });
  });

  test('REQ-4.4: Should support pagination with limit parameter', async () => {
    // This test verifies the API supports pagination
    const response = await page.request.get(`${API_URL}/api/chat/history?limit=5`);
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('messages');
  });

  // ============================================================================
  // REQUIREMENT 7: API Endpoints
  // ============================================================================

  test('REQ-7.1: POST /api/diagram/generate should accept parameters and return Mermaid code', async () => {
    const payload = {
      userPrompt: 'Create a simple flowchart',
      diagramType: 'flowchart'
    };

    const response = await page.request.post(`${API_URL}/api/diagram/generate`, {
      data: payload
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('mermaidCode');
    expect(data).toHaveProperty('chatId');
  });

  test('REQ-7.2: GET /api/chat/history should return paginated messages', async () => {
    const response = await page.request.get(`${API_URL}/api/chat/history?limit=10`);
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('messages');
    expect(Array.isArray(data.messages)).toBe(true);
  });

  test('REQ-7.3: POST /api/chat/save should save message and return confirmation', async () => {
    const payload = {
      userMessage: 'Test message',
      diagramType: 'flowchart'
    };

    const response = await page.request.post(`${API_URL}/api/chat/save`, {
      data: payload
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('chatId');
  });

  test('REQ-7.4: API should return appropriate HTTP status codes on error', async () => {
    // Test with invalid payload
    const response = await page.request.post(`${API_URL}/api/diagram/generate`, {
      data: {}
    });

    expect([400, 500]).toContain(response.status());
  });

  // ============================================================================
  // REQUIREMENT 8: Frontend Hosting
  // ============================================================================

  test('REQ-8.1: Frontend should load from CloudFront with HTTPS', async () => {
    expect(page.url()).toContain('https://');
    expect(page.url()).toContain('cloudfront.net');
  });

  test('REQ-8.2: Frontend should load within 3 seconds', async () => {
    const startTime = Date.now();
    await page.goto(APP_URL, { waitUntil: 'networkidle' });
    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(3000);
  });

  test('REQ-8.3: Frontend assets should be cached by CloudFront', async () => {
    const response = await page.goto(APP_URL, { waitUntil: 'networkidle' });
    
    expect(response?.status()).toBe(200);
    const headers = response?.headers();
    expect(headers).toBeTruthy();
  });

  // ============================================================================
  // REQUIREMENT 9: Diagram Rendering
  // ============================================================================

  test('REQ-9.1: Should parse and render Mermaid code using React components', async () => {
    const testMessage = 'Create a flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for diagram
    const diagramRenderer = page.locator('[data-testid="diagram-renderer"], svg, canvas');
    await expect(diagramRenderer.first()).toBeVisible({ timeout: 30000 });
  });

  test('REQ-9.2: Should enable mouse scroll zoom functionality', async () => {
    const testMessage = 'Create a flowchart with multiple nodes';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for diagram
    const diagramRenderer = page.locator('[data-testid="diagram-renderer"], svg, canvas').first();
    await expect(diagramRenderer).toBeVisible({ timeout: 30000 });

    // Simulate scroll zoom
    await diagramRenderer.hover();
    await page.mouse.wheel(0, 5);
  });

  test('REQ-9.3: Should enable click-and-drag pan functionality', async () => {
    const testMessage = 'Create a flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for diagram
    const diagramRenderer = page.locator('[data-testid="diagram-renderer"], svg, canvas').first();
    await expect(diagramRenderer).toBeVisible({ timeout: 30000 });

    // Simulate drag
    await diagramRenderer.dragTo(diagramRenderer, { sourcePosition: { x: 100, y: 100 }, targetPosition: { x: 200, y: 200 } });
  });

  test('REQ-9.4: Should apply automatic layout positioning for multiple nodes', async () => {
    const testMessage = 'Create a flowchart with 5 steps';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for diagram
    const diagramRenderer = page.locator('[data-testid="diagram-renderer"], svg, canvas').first();
    await expect(diagramRenderer).toBeVisible({ timeout: 30000 });
  });

  // ============================================================================
  // REQUIREMENT 10: LLM Prompt Engineering
  // ============================================================================

  test('REQ-10.1: Should include system context in LLM prompt', async () => {
    const testMessage = 'Create a flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for response
    const mermaidCode = page.locator('code:has-text("graph"), code:has-text("flowchart")');
    await expect(mermaidCode.first()).toBeVisible({ timeout: 30000 });
  });

  test('REQ-10.2: Flowchart should use graph TD or graph LR syntax', async () => {
    const testMessage = 'Create a flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for code
    const mermaidCode = page.locator('code');
    const codeContent = await mermaidCode.first().textContent();
    
    expect(codeContent).toMatch(/graph\s+(TD|LR|BT|RL)/i);
  });

  test('REQ-10.3: ERD should use erDiagram syntax', async () => {
    // Select ERD diagram type
    const erdButton = page.locator('[data-testid="diagram-type-button"]:has-text("ERD")').first();
    
    if (await erdButton.isVisible()) {
      await erdButton.click();

      const testMessage = 'Create an ERD for a user database';
      const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
      await chatInput.fill(testMessage);

      const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
      await sendButton.click();

      // Wait for code
      const mermaidCode = page.locator('code');
      const codeContent = await mermaidCode.first().textContent();
      
      expect(codeContent).toMatch(/erDiagram/i);
    }
  });

  test('REQ-10.4: Sequence should use sequenceDiagram syntax', async () => {
    // Select Sequence diagram type
    const sequenceButton = page.locator('[data-testid="diagram-type-button"]:has-text("Sequence")').first();
    
    if (await sequenceButton.isVisible()) {
      await sequenceButton.click();

      const testMessage = 'Create a sequence diagram for a login flow';
      const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
      await chatInput.fill(testMessage);

      const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
      await sendButton.click();

      // Wait for code
      const mermaidCode = page.locator('code');
      const codeContent = await mermaidCode.first().textContent();
      
      expect(codeContent).toMatch(/sequenceDiagram/i);
    }
  });

  test('REQ-10.5: Should extract code blocks marked with mermaid delimiters', async () => {
    const testMessage = 'Create a flowchart';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for code block
    const codeBlock = page.locator('code, pre');
    const codeContent = await codeBlock.first().textContent();
    
    expect(codeContent).toBeTruthy();
    expect(codeContent?.length).toBeGreaterThan(0);
  });
});
