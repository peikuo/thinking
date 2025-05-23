"""
Direct test script for calling all four AI models with a Chinese prompt.
This script makes actual API calls and prints the responses.
"""
import asyncio
import json
import os
import sys
from datetime import datetime

# Add the project root to the path so we can import the modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from backend.env_config import get_api_key
# Now we can import from the backend package
from backend.utils.model_helpers import (call_deepseek, call_doubao, call_glm,
                                         call_grok, call_openai, call_qwen)

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
    
    try:
        # Get the API key
        api_key = get_api_key(model_name.lower())
        if not api_key:
            print(f"No API key found for {model_name}")
            return f"Error: No API key found for {model_name}"
        
        if streaming:
            # For streaming mode, we need to handle the response differently
            print(f"\nStreaming response from {model_name}:")
            response = await api_function(TEST_MESSAGES, api_key, use_streaming=True)
            
            # If it's a StreamingResponse, we need to extract the content
            if hasattr(response, 'body_iterator'):
                full_content = ""
                async for chunk in response.body_iterator:
                    try:
                        # Handle both bytes and string types
                        if isinstance(chunk, bytes):
                            chunk_str = chunk.decode('utf-8')
                        else:
                            chunk_str = str(chunk)
                            
                        if chunk_str.startswith('data: '):
                            try:
                                data = json.loads(chunk_str[6:])
                                if 'content' in data:
                                    content = data['content']
                                    full_content += content
                                    print(content, end='', flush=True)
                            except json.JSONDecodeError:
                                pass
                    except Exception as e:
                        print(f"Error processing chunk: {str(e)}")
                        continue
                print()  # Add a newline at the end
                return full_content
            else:
                # If it's not a StreamingResponse, just return it
                print(response)
                return response
        else:
            # Call the API in non-streaming mode
            result = await api_function(TEST_MESSAGES, api_key, use_streaming=False)
            
            # Print the result
            print(f"\nResponse from {model_name}:")
            print(result)
            
            return result
    except Exception as e:
        error_message = f"Error calling {model_name} API: {str(e)}"
        print(error_message)
        return error_message

async def main():
    """Test all four models and save the responses."""
    # Configuration is loaded from environment variables automatically
    
    # Determine if we should use streaming mode
    import argparse
    parser = argparse.ArgumentParser(description="Test LLM APIs with streaming")
    parser.add_argument("--stream", action="store_true", default=True, help="Use streaming mode")
    parser.add_argument("--model", type=str, help="Model to test (openai, glm, doubao, grok, qwen, deepseek, all)")
    args = parser.parse_args()
    streaming_mode = args.stream
    
    print(f"=== Testing All Models with Chinese Prompt: '{TEST_PROMPT}' ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Streaming mode: {streaming_mode}")
    
    # Define the models and their API functions
    all_models = {
        # "doubao": ("Doubao", call_doubao),
        # "glm": ("GLM", call_glm),
        "openai": ("OpenAI", call_openai),
        # "grok": ("Grok", call_grok),
        # "qwen": ("Qwen", call_qwen),
        # "deepseek": ("DeepSeek", call_deepseek)
    }
    
    # Test specific model or all models
    responses = {}
    if args.model and args.model.lower() != "all":
        if args.model.lower() in all_models:
            model_key = args.model.lower()
            model_name, api_function = all_models[model_key]
            response = await test_model(model_name, api_function, streaming=streaming_mode)
            responses[model_key] = response
        else:
            print(f"Model {args.model} not found. Available models: {', '.join(all_models.keys())}")
    else:
        # Test all models
        for model_key, (model_name, api_function) in all_models.items():
            response = await test_model(model_name, api_function, streaming=streaming_mode)
            responses[model_key] = response
    
    # Create responses directory if it doesn't exist
    responses_dir = os.path.join(os.path.dirname(__file__), "responses")
    os.makedirs(responses_dir, exist_ok=True)
    
    # Save responses to a file in the responses directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(responses_dir, f"model_responses_{TEST_LANGUAGE}_{timestamp}.json")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
    
    print(f"\n\nResponses saved to: {output_file}")
    
    # Print a summary
    print("\n=== Response Summary ===")
    for model_name in responses:
        response = responses[model_name]
        # Truncate long responses for the summary
        summary = response[:200] + "..." if len(response) > 200 else response
        print(f"{model_name.capitalize()}: {summary}")

if __name__ == "__main__":
    asyncio.run(main())
