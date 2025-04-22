# This file was renamed from test_models_direct.py to manual_test_models_direct.py
# to prevent it from running in CI/CD environments.
from datetime import datetime

# Test prompt in Chinese asking about recent international news
TEST_PROMPT = "最近有什么国际新闻"
TEST_MESSAGES = [{"role": "user", "content": TEST_PROMPT}]

# Test language (en or zh)
TEST_LANGUAGE = "zh"  # Use Chinese for testing

async def test_model(model_name, api_function, streaming=False):
    """Test a specific model with the Chinese prompt."""
    print(f"\n\n=== Testing {model_name} API ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Prompt: {TEST_PROMPT}")
    print(f"Language: {TEST_LANGUAGE}")
    print(f"Streaming mode: {streaming}")
    print("Waiting for response...")
    # ... rest of your manual testing logic ...
