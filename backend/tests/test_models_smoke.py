"""
Basic smoke tests for CI/CD.
These tests do not call external APIs or require special credentials.
They just verify that the test framework and core backend functions are importable and working.
"""
import importlib


def test_import_main():
    """Test that the backend main module can be imported."""
    main = importlib.import_module("backend.main")
    assert hasattr(main, "app")

def test_import_utils():
    """Test that the backend utils.model_prompts module can be imported and has get_model_prompt."""
    model_prompts = importlib.import_module("backend.utils.model_prompts")
    assert hasattr(model_prompts, "get_model_prompt")
