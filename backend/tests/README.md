# Backend Tests for Thinking Website

This directory contains test cases for the backend API integrations of the Thinking Website. The tests focus on verifying the functionality of the four model API integrations: OpenAI, Grok, Qwen, and DeepSeek.

## Test Structure

- `test_openai_api.py`: Tests for the OpenAI API integration
- `test_grok_api.py`: Tests for the Grok API integration
- `test_qwen_api.py`: Tests for the Qwen API integration
- `test_deepseek_api.py`: Tests for the DeepSeek API integration
- `conftest.py`: Shared fixtures and configuration for tests

## Running Tests

To run all tests:

```bash
cd /path/to/thinking/backend
python -m pytest tests/
```

To run tests for a specific API:

```bash
python -m pytest tests/test_openai_api.py
```

## Test Coverage

Each API test file includes tests for:

1. Using a user-provided API key
2. Falling back to environment variable API keys
3. Handling error responses
4. Handling missing API keys

## Dependencies

The tests require:

- pytest
- pytest-asyncio (for testing async functions)
- unittest.mock (for mocking API responses)

## Adding New Tests

When adding new tests, follow these guidelines:

1. Create a new test file if testing a new component
2. Use the existing fixtures in conftest.py
3. Follow the pattern of mocking external API calls
4. Ensure all tests are properly isolated
