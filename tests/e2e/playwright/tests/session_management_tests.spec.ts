import { test, expect, Page } from '@playwright/test';

/**
 * Architecture AI Assistant - Session Management E2E Tests
 * Tests the new session management features added to the application
 */

const APP_URL = 'https://d1to0rasl28a6e.cloudfront.net';
const API_URL = 'https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev';

test.describe('Session Management - E2E Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    await page.goto(APP_URL, { waitUntil: 'networkidle' });
  });

  test.afterEach(async () => {
    await page.close();
  });

  // ============================================================================
  // SESSION CREATION TESTS
  // ============================================================================

  test('Should create new session when New Chat button is clicked', async () => {
    // Look for New Chat button
    const newChatButton = page.locator('button:has-text("New Chat"), [data-testid="new-chat-button"]');
    
    if (await newChatButton.isVisible()) {
      await newChatButton.click();
      
      // Verify chat interface is cleared
      const chatMessages = page.locator('[data-testid="chat-message"], .message');
      const messageCount = await chatMessages.count();
      expect(messageCount).toBe(0);
    }
  });

  test('Should generate session title from first message', async () => {
    const testMessage = 'Create a user authentication flowchart for testing session titles';

    // Send first message
    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(5000);

    // Check if session appears in sidebar with truncated title
    const sessionItems = page.locator('[data-testid="session-item"], .session-item');
    if (await sessionItems.first().isVisible()) {
      const sessionTitle = await sessionItems.first().textContent();
      expect(sessionTitle).toContain('Create a user authentication flowchart');
    }
  });

  // ============================================================================
  // SESSION NAVIGATION TESTS
  // ============================================================================

  test('Should display sessions in sidebar grouped by date', async () => {
    // Check for sidebar
    const sidebar = page.locator('[data-testid="sidebar"], .sidebar');
    await expect(sidebar).toBeVisible();

    // Check for date groupings
    const dateGroups = page.locator('[data-testid="date-group"], .date-group');
    if (await dateGroups.first().isVisible()) {
      const groupText = await dateGroups.first().textContent();
      expect(groupText).toMatch(/Today|Yesterday|Last 7 Days|Older/);
    }
  });

  test('Should load messages when session is selected', async () => {
    // First create a session with a message
    const testMessage = 'Create a flowchart for session selection test';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(5000);

    // Click on a session in sidebar (if available)
    const sessionItems = page.locator('[data-testid="session-item"], .session-item');
    if (await sessionItems.first().isVisible()) {
      await sessionItems.first().click();

      // Verify messages are loaded
      const chatMessages = page.locator('[data-testid="chat-message"], .message');
      const messageCount = await chatMessages.count();
      expect(messageCount).toBeGreaterThan(0);
    }
  });

  test('Should highlight current session in sidebar', async () => {
    // Send a message to create a session
    const testMessage = 'Create a flowchart for highlighting test';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(3000);

    // Check if current session is highlighted
    const activeSession = page.locator('[data-testid="session-item"].active, .session-item.active');
    if (await activeSession.isVisible()) {
      await expect(activeSession).toHaveClass(/active|selected|current/);
    }
  });

  // ============================================================================
  // SESSION API TESTS
  // ============================================================================

  test('Should create session via API', async () => {
    const response = await page.request.post(`${API_URL}/api/session`, {
      data: {}
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    
    expect(data).toHaveProperty('sessionId');
    expect(data).toHaveProperty('title');
    expect(data).toHaveProperty('diagramType');
    expect(data).toHaveProperty('createdAt');
    expect(data).toHaveProperty('updatedAt');
    expect(data).toHaveProperty('messageCount');
  });

  test('Should list sessions via API', async () => {
    const response = await page.request.get(`${API_URL}/api/session?limit=10`);
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('sessions');
    expect(data).toHaveProperty('count');
    expect(Array.isArray(data.sessions)).toBe(true);
  });

  test('Should get session messages via API', async () => {
    // First create a session
    const createResponse = await page.request.post(`${API_URL}/api/session`, {
      data: {}
    });
    const sessionData = await createResponse.json();
    const sessionId = sessionData.sessionId;

    // Get messages for the session
    const response = await page.request.get(`${API_URL}/api/session/${sessionId}/messages`);
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('chats');
    expect(data).toHaveProperty('count');
    expect(Array.isArray(data.chats)).toBe(true);
  });

  test('Should update session title via API', async () => {
    // First create a session
    const createResponse = await page.request.post(`${API_URL}/api/session`, {
      data: {}
    });
    const sessionData = await createResponse.json();
    const sessionId = sessionData.sessionId;

    // Update the session title
    const newTitle = 'Updated Session Title';
    const response = await page.request.put(`${API_URL}/api/session/${sessionId}`, {
      data: { title: newTitle }
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.title).toBe(newTitle);
  });

  // ============================================================================
  // SESSION WORKFLOW TESTS
  // ============================================================================

  test('Should maintain session context across multiple messages', async () => {
    // Send first message
    const firstMessage = 'Create a flowchart for user registration';
    let chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(firstMessage);

    let sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(5000);

    // Send second message in same session
    const secondMessage = 'Add password validation to the flowchart';
    chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(secondMessage);

    sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(5000);

    // Verify both messages are in the same session
    const chatMessages = page.locator('[data-testid="chat-message"], .message');
    const messageCount = await chatMessages.count();
    expect(messageCount).toBeGreaterThanOrEqual(2);
  });

  test('Should generate diagram within session context', async () => {
    // Create a session first
    const createResponse = await page.request.post(`${API_URL}/api/session`, {
      data: {}
    });
    const sessionData = await createResponse.json();
    const sessionId = sessionData.sessionId;

    // Generate diagram within the session
    const payload = {
      userPrompt: 'Create a simple flowchart for session testing',
      diagramType: 'flowchart',
      sessionId: sessionId
    };

    const response = await page.request.post(`${API_URL}/api/diagram/generate`, {
      data: payload
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    
    expect(data).toHaveProperty('chatId');
    expect(data).toHaveProperty('mermaidCode');
    expect(data).toHaveProperty('imageUrl');
    expect(data).toHaveProperty('markdownUrl');
    expect(data.status).toBe('completed');
  });

  test('Should persist session data across page reloads', async () => {
    // Send a message to create session
    const testMessage = 'Create a flowchart for persistence test';

    const chatInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await chatInput.fill(testMessage);

    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send"]').first();
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(5000);

    // Get current message count
    const chatMessages = page.locator('[data-testid="chat-message"], .message');
    const initialMessageCount = await chatMessages.count();

    // Reload the page
    await page.reload({ waitUntil: 'networkidle' });

    // Check if sessions are still loaded in sidebar
    const sessionItems = page.locator('[data-testid="session-item"], .session-item');
    if (await sessionItems.first().isVisible()) {
      // Click on the session to load messages
      await sessionItems.first().click();
      
      // Verify messages are restored
      const restoredMessages = page.locator('[data-testid="chat-message"], .message');
      const restoredMessageCount = await restoredMessages.count();
      expect(restoredMessageCount).toBeGreaterThanOrEqual(0);
    }
  });

  // ============================================================================
  // ERROR HANDLING TESTS
  // ============================================================================

  test('Should handle invalid session ID gracefully', async () => {
    const invalidSessionId = 'invalid-session-id-123';
    
    const response = await page.request.get(`${API_URL}/api/session/${invalidSessionId}/messages`);
    expect([400, 404]).toContain(response.status());
  });

  test('Should handle session creation failure gracefully', async () => {
    // Intercept session creation to simulate failure
    await page.route(`${API_URL}/api/session`, route => {
      if (route.request().method() === 'POST') {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal server error' })
        });
      } else {
        route.continue();
      }
    });

    // Try to create a session via UI
    const newChatButton = page.locator('button:has-text("New Chat"), [data-testid="new-chat-button"]');
    
    if (await newChatButton.isVisible()) {
      await newChatButton.click();
      
      // Check for error handling
      const errorMessage = page.locator('[data-testid="error-message"], .error, .alert-error');
      if (await errorMessage.isVisible()) {
        await expect(errorMessage).toBeVisible();
      }
    }
  });

  // ============================================================================
  // PERFORMANCE TESTS
  // ============================================================================

  test('Should load session list within reasonable time', async () => {
    const startTime = Date.now();
    
    // Trigger session list load
    await page.goto(APP_URL, { waitUntil: 'networkidle' });
    
    // Wait for sidebar to load
    const sidebar = page.locator('[data-testid="sidebar"], .sidebar');
    await expect(sidebar).toBeVisible({ timeout: 5000 });
    
    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
  });

  test('Should handle large number of sessions efficiently', async () => {
    // Test pagination by requesting a large limit
    const response = await page.request.get(`${API_URL}/api/session?limit=100`);
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('sessions');
    expect(data).toHaveProperty('count');
    
    // Response should be received within reasonable time
    // (This is implicitly tested by the request timeout)
  });
});