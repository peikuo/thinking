# Thinking Backend

This is the FastAPI backend for the Thinking project, which provides API endpoints to query multiple AI models in parallel and summarize their responses.

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file by copying the `.env.example` file:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file and add your API keys for OpenAI, Grok, Qwen, and DeepSeek.

## Running the Server

Start the FastAPI server with:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

## API Endpoints

- `POST /api/chat` - Send a conversation to all AI models and get their responses along with a summary
- `POST /api/summary` - Generate a summary of multiple AI responses
- `GET /api/health` - Health check endpoint

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
