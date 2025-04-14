# Environment Variable Configuration Guide

This document explains how to use the environment variable-based configuration system for the Thinking Website backend.

## Overview

The backend supports three distinct environments:
- **dev**: Development environment
- **test**: Testing environment
- **prd**: Production environment

All configuration is now managed through environment variables, which can be set either directly in your system or through a `.env` file.

## Environment Variables

The following environment variables are supported:

### Environment Selection

- `THINKING_ENV`: Sets the current environment (dev, test, or prd). Default: `dev`

### API Keys

- `OPENAI_API_KEY`: OpenAI API key
- `GROK_API_KEY`: Grok API key
- `QWEN_API_KEY`: Qwen API key
- `DEEPSEEK_API_KEY`: DeepSeek API key

### API URLs (optional)

- `OPENAI_API_URL`: OpenAI API URL. Default: `https://api.openai.com/v1/chat/completions`
- `GROK_API_URL`: Grok API URL. Default: `https://api.x.ai/v1`
- `QWEN_API_URL`: Qwen API URL. Default: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `DEEPSEEK_API_URL`: DeepSeek API URL. Default: `https://api.deepseek.com`

### Logging Configuration

- `LOG_LEVEL`: Sets the logging verbosity level. Values: `debug`, `info`, `warning`, `error`, `critical`. Default: `info`

### Models (optional)

- `OPENAI_MODEL`: OpenAI model to use. Default: `gpt-4o-mini`
- `GROK_MODEL`: Grok model to use. Default: `grok-2-latest`
- `QWEN_MODEL`: Qwen model to use. Default: `qwen-plus`
- `DEEPSEEK_MODEL`: DeepSeek model to use. Default: `deepseek-chat`

### Server Configuration (optional)

- `SERVER_HOST`: Host to bind the server to. Default: `localhost`
- `SERVER_PORT`: Port to bind the server to. Default: `8000`
- `SERVER_DEBUG`: Whether to enable debug mode. Default: `true` in dev, `false` in prod
- `LOG_LEVEL`: Logging level. Default: `debug` in dev, `info` in prod

## Setting Environment Variables

There are several ways to set environment variables:

### 1. Using a .env File (Recommended)

Create a `.env` file in the backend directory:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your settings
vim .env  # or use any text editor
```

The `.env` file should contain your environment variables:

```bash
# Environment
THINKING_ENV=dev

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GROK_API_KEY=your_grok_api_key_here
QWEN_API_KEY=your_qwen_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Other settings as needed...
```

### 2. System Environment Variables

Set environment variables directly in your system:

```bash
# For development
export THINKING_ENV=dev
export OPENAI_API_KEY=your_openai_api_key_here
# ... other variables as needed

# Then start the server
python main.py
```

### 3. API Endpoint

Switch environments dynamically using the API:

```bash
# Using curl
curl -X POST http://localhost:8000/api/switch-environment/prd

# Response
{
  "status": "success",
  "message": "Switched to prd environment and reloaded configuration",
  "environment": "prd"
}
```

## Logging System

The backend includes a comprehensive logging system that provides detailed information about application operations, API requests, and errors.

### Log Types

- **Application Logs**: General information about application operations
- **Request Logs**: Detailed information about API requests in JSON format
- **Error Logs**: Detailed information about errors with stack traces

### Log Directories

Logs are stored in the following directories:

- `backend/logs/app`: Application logs
- `backend/logs/requests`: API request logs
- `backend/logs/errors`: Error logs
- `backend/logs/archived`: Archived logs

### Log Rotation

Logs are automatically rotated daily and archived after 30 days. The archiving process compresses old logs to save disk space.

### Log Levels

The logging system supports the following log levels, in order of increasing severity:

- `debug`: Detailed debugging information
- `info`: General information messages
- `warning`: Warning messages
- `error`: Error messages
- `critical`: Critical error messages

You can set the log level using the `LOG_LEVEL` environment variable or through the API endpoints.

## API Endpoints for Configuration Management

The following endpoints are available for managing configuration:

### Get Current Environment

```
GET /api/current-environment
```

Returns the current environment and server configuration.

### Reload Configuration

```
POST /api/reload-config
```

### Get Current Log Level

```
GET /api/logs/level
```

Returns the current log level.

### Set Log Level

```
POST /api/logs/level/{level}
```

Sets the log level. The `level` parameter must be one of: `debug`, `info`, `warning`, `error`, `critical`.

Reloads the configuration from environment variables. This is useful if you've updated your `.env` file or system environment variables and want to apply the changes without restarting the server.

### Switch Environment

```
POST /api/switch-environment/{env}
```

Switches to the specified environment (dev, test, or prd). This sets the `THINKING_ENV` variable in memory (not in your `.env` file) and reloads the configuration.

## Best Practices

1. **Keep API Keys Secure**: Never commit your `.env` file to version control. Always add it to your `.gitignore` file.

2. **Environment-Specific Settings**: Use different settings for different environments:
   - Development: Use lower-tier models and enable debugging
   - Production: Use higher-tier models and disable debugging

3. **Deployment**: When deploying to production, set environment variables through your hosting platform's configuration interface rather than using a `.env` file.

4. **Backup**: Keep a backup of your API keys in a secure location.

## Troubleshooting

If you encounter issues with the configuration:

1. Check that your `.env` file exists and contains the necessary variables
2. Verify that the environment variables are correctly formatted
3. Use the `/api/reload-config` endpoint to reload the configuration
4. Check the server logs for any error messages related to configuration loading

## Customizing Configuration

To customize the configuration for an environment:

1. Edit your `.env` file or set environment variables directly in your system
2. Alternatively, you can create configuration files in the `.config/` directory (which is gitignored for security)
3. Reload the configuration using the `/api/reload-config` endpoint or by restarting the server

## Environment-Specific Configurations

You can use different configurations for different environments by setting the `THINKING_ENV` variable:

- **Development (dev)**:
  ```bash
  THINKING_ENV=dev
  OPENAI_MODEL=gpt-4o-mini  # Use smaller models to save costs
  SERVER_DEBUG=true
  LOG_LEVEL=debug
  ```

- **Testing (test)**:
  ```bash
  THINKING_ENV=test
  OPENAI_MODEL=gpt-4o-mini
  SERVER_DEBUG=false
  LOG_LEVEL=info
  ```

- **Production (prd)**:
  ```bash
  THINKING_ENV=prd
  OPENAI_MODEL=gpt-4o  # Use more powerful models in production
  SERVER_DEBUG=false
  LOG_LEVEL=info
  ```

## Security Considerations

- Never commit your `.env` file to version control (add it to `.gitignore`)
- For production deployments, set environment variables through your hosting platform's configuration interface
- Consider using a secrets management service for API keys in production environments
- Restrict access to the configuration management endpoints in production
