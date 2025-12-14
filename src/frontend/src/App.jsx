import { useState } from 'react'
import './App.css'

// API Gateway URL from Terraform outputs
const API_BASE_URL = 'https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev'

function App() {
  const [testResults, setTestResults] = useState([])
  const [loading, setLoading] = useState(false)

  const addResult = (test, success, message) => {
    setTestResults(prev => [...prev, { test, success, message, timestamp: new Date().toISOString() }])
  }

  const testGenerateDiagram = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/diagram/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userPrompt: 'Create a simple flowchart',
          diagramType: 'flowchart'
        })
      })
      
      const data = await response.json()
      addResult('Generate Diagram', response.ok, `Status: ${response.status}, Response: ${JSON.stringify(data).substring(0, 100)}...`)
    } catch (error) {
      addResult('Generate Diagram', false, `Error: ${error.message}`)
    }
    setLoading(false)
  }

  const testSaveChat = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chatId: `test-${Date.now()}`,
          userMessage: 'Test message',
          diagramType: 'flowchart'
        })
      })
      
      const data = await response.json()
      addResult('Save Chat', response.ok, `Status: ${response.status}, Response: ${JSON.stringify(data)}`)
    } catch (error) {
      addResult('Save Chat', false, `Error: ${error.message}`)
    }
    setLoading(false)
  }

  const testGetHistory = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/history?limit=10`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      const data = await response.json()
      addResult('Get History', response.ok, `Status: ${response.status}, Response: ${JSON.stringify(data).substring(0, 100)}...`)
    } catch (error) {
      addResult('Get History', false, `Error: ${error.message}`)
    }
    setLoading(false)
  }

  const clearResults = () => {
    setTestResults([])
  }

  return (
    <div className="App">
      <h1>Architecture AI Assistant - Integration Test</h1>
      <p>API Base URL: {API_BASE_URL}</p>
      
      <div className="test-buttons">
        <button onClick={testGenerateDiagram} disabled={loading}>
          Test Generate Diagram
        </button>
        <button onClick={testSaveChat} disabled={loading}>
          Test Save Chat
        </button>
        <button onClick={testGetHistory} disabled={loading}>
          Test Get History
        </button>
        <button onClick={clearResults} disabled={loading}>
          Clear Results
        </button>
      </div>

      {loading && <p>Loading...</p>}

      <div className="test-results">
        <h2>Test Results</h2>
        {testResults.length === 0 ? (
          <p>No tests run yet. Click a button above to test an endpoint.</p>
        ) : (
          <ul>
            {testResults.map((result, index) => (
              <li key={index} className={result.success ? 'success' : 'error'}>
                <strong>{result.test}</strong>: {result.success ? '✓ Success' : '✗ Failed'}
                <br />
                <small>{result.message}</small>
                <br />
                <small>{result.timestamp}</small>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

export default App
