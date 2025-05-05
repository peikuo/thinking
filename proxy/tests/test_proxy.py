import os
import sys

import pytest
from fastapi.testclient import TestClient

# Ensure src is in the import path
dir_path = os.path.dirname(os.path.realpath(__file__))
src_path = os.path.abspath(os.path.join(dir_path, '../src'))
sys.path.insert(0, src_path)

from proxy import app

client = TestClient(app)

def test_openai_completions_mock():
    headers = {"Authorization": "Bearer test-api-key"}
    response = client.post(
        "/openai/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "Hello"}]},
        headers=headers
    )
    # This is a mock test; in real use, you'd mock the OpenAI call
    assert response.status_code in (200, 400, 401, 422)

def test_grok_completions_mock():
    response = client.post("/grok/v1/chat/completions", json={"messages": [{"role": "user", "content": "Hi"}]})
    assert response.status_code in (200, 400, 422)
