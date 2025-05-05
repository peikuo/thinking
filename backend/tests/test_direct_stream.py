"""
Test script for the direct streaming implementations.
This script tests the direct streaming implementations without the complex nesting
that causes the 'coroutine was never awaited' warnings.
"""
import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the direct streaming implementations
from tests.direct_streaming import (direct_deepseek_stream,
                                    direct_doubao_stream, direct_glm_stream,
                                    direct_grok_stream, direct_openai_stream,
                                    direct_qwen_stream)

# Test messages
TEST_MESSAGES_EN = [{"role": "user", "content": "What are some recent international news?"}]
TEST_MESSAGES_ZH = [{"role": "user", "content": "最近有什么国际新闻"}]

async def test_model(model_name: str, api_function: Callable, streaming: bool = False):
    """Test a model with the given API function"""
    print(f"\n=== Testing {model_name} API ===")
    
    # Use Chinese test messages
    test_messages = TEST_MESSAGES_ZH
    language = "zh"
    
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Prompt: {test_messages[0]['content']}")
    print(f"Language: {language}")
    print(f"Streaming mode: {streaming}")
    print("Waiting for response...\n")
    
    try:
        # Call the API function with streaming mode
        response = await api_function(test_messages, language=language)
        
        # If it's a StreamingResponse, we need to extract the content
        if hasattr(response, 'body_iterator'):
            full_content = ""
            print(f"Streaming response from {model_name}:")
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
            # For non-streaming responses
            print(f"Response from {model_name}:")
            print(response)
            return response
    except Exception as e:
        error_msg = f"Error calling {model_name} API: {str(e)}"
        print(error_msg)
        return error_msg

async def main():
    """Main function to test all models"""
    parser = argparse.ArgumentParser(description="Test LLM APIs with streaming")
    parser.add_argument("--model", type=str, help="Model to test (openai, glm, doubao, grok, qwen, deepseek, all)")
    args = parser.parse_args()
    
    print(f"=== Testing Direct Streaming Implementations ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define the models and their API functions
    models = {
        "openai": direct_openai_stream,
        "glm": direct_glm_stream,
        "doubao": direct_doubao_stream,
        "grok": direct_grok_stream,
        "qwen": direct_qwen_stream,
        "deepseek": direct_deepseek_stream
    }
    
    responses = {}
    
    # Test the specified model or all models
    if args.model and args.model.lower() != "all":
        if args.model.lower() in models:
            model_name = args.model.lower()
            api_function = models[model_name]
            response = await test_model(model_name.capitalize(), api_function)
            responses[model_name] = response
        else:
            print(f"Model {args.model} not found. Available models: {', '.join(models.keys())}")
    else:
        # Test all models
        for model_name, api_function in models.items():
            response = await test_model(model_name.capitalize(), api_function)
            responses[model_name] = response
    
    # Create responses directory if it doesn't exist
    responses_dir = os.path.join(os.path.dirname(__file__), "responses")
    os.makedirs(responses_dir, exist_ok=True)
    
    # Save responses to a file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(responses_dir, f"direct_streaming_responses_zh_{timestamp}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
    
    print(f"\nResponses saved to: {filename}")
    
    # Print a summary of the responses
    print("\n=== Response Summary ===")
    for model, response in responses.items():
        # Truncate long responses for the summary
        if isinstance(response, str) and len(response) > 100:
            response = response[:100] + "..."
        print(f"{model.capitalize()}: {response}")

if __name__ == "__main__":
    asyncio.run(main())
