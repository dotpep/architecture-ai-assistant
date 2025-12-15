# Generate Diagram Lambda Function

This Lambda function handles diagram generation requests from the Architecture AI Assistant frontend.

## Components

### lambda_function.py
Main Lambda handler that:
- Validates incoming requests (userPrompt and diagramType)
- Calls LLM API with constructed prompts
- Extracts and validates Mermaid code from LLM response
- Saves diagrams to S3 (markdown and PNG)
- Stores metadata in DynamoDB
- Returns CloudFront URLs for diagram access

**Requirements**: 2.1, 5.1, 5.2, 5.3, 7.1

### mermaid_validator.py
Validates Mermaid diagram syntax:
- Checks for valid diagram type declarations
- Performs type-specific validation (flowchart, ER, sequence, class, state)
- Validates balanced brackets and braces
- Ensures diagrams have required elements (nodes, relationships, etc.)

**Requirements**: 2.5, 5.4

### mermaid_extractor.py
Extracts Mermaid code from LLM responses:
- Parses ```mermaid code blocks
- Handles multiple code blocks (returns first valid one)
- Cleans code by removing fence markers
- Validates basic structure

**Requirements**: 5.3, 10.5

### prompt_builder.py
Builds LLM prompts with diagram-type-specific instructions:
- Contains Mermaid syntax rules for each diagram type
- Constructs system and user prompts
- Ensures LLM generates valid Mermaid code

**Requirements**: 5.2, 10.1, 10.2, 10.3, 10.4

### diagram_renderer.py
Renders Mermaid diagrams to PNG images:
- Currently generates placeholder PNG images
- Can be extended to use mermaid-cli or rendering service
- Saves both markdown and PNG to S3

**Requirements**: 3.1, 3.2

## Environment Variables

Required environment variables (set by Terraform):
- `DYNAMODB_TABLE_NAME`: DynamoDB table for chat history
- `S3_BUCKET_NAME`: S3 bucket for diagram storage
- `CLOUDFRONT_URL`: CloudFront distribution URL
- `LLM_API_ENDPOINT`: LLM API endpoint URL
- `LLM_API_KEY`: LLM API authentication key
- `LLM_MODEL` (optional): LLM model name (default: gpt-3.5-turbo)

## API Request Format

```json
{
  "userPrompt": "Create a flowchart for user login",
  "diagramType": "flowchart"
}
```

Supported diagram types:
- `flowchart` - Flowchart diagrams
- `erdiagram` - Entity-Relationship diagrams
- `sequence` - Sequence diagrams
- `class` - Class diagrams
- `state` - State diagrams
- `architecture` - High-level architecture diagrams
- `dfd` - Data Flow Diagrams

## API Response Format

Success (200):
```json
{
  "chatId": "uuid",
  "timestamp": 1702564800,
  "mermaidCode": "graph TD\n  A --> B",
  "imageUrl": "https://cloudfront-url/diagrams/uuid.png",
  "markdownUrl": "https://cloudfront-url/diagrams/uuid.md",
  "status": "completed"
}
```

Error (400/500/502):
```json
{
  "error": "Error message"
}
```

## Testing

Run the test suite:
```bash
python tests/unit/test_mermaid_components.py
```

This tests:
- Request validation
- Mermaid code validation (all diagram types)
- Mermaid code extraction from LLM responses
- Prompt building for all diagram types
- Response formatting

## Deployment

The Lambda function is deployed via Terraform. To update:

1. Make code changes
2. Package the function with dependencies
3. Run `terraform apply` to update

The function uses a Lambda layer for shared dependencies (boto3, requests, etc.).

## Future Enhancements

1. **PNG Rendering**: Integrate mermaid-cli or external rendering service for actual diagram images
2. **Caching**: Cache LLM responses for identical prompts
3. **Retry Logic**: Add exponential backoff for LLM API failures
4. **Streaming**: Support streaming responses for large diagrams
5. **Validation**: Add more sophisticated Mermaid syntax validation
