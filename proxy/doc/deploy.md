# Proxy Service Deployment Guide

## Prerequisites
- Python 3.8+
- [uv](https://github.com/astral-sh/uv) for virtual environment management (recommended)
- Install dependencies: `pip install -r requirements.txt`
- Set required environment variables:
  - `OPENAI_API_URL` (e.g., https://api.openai.com/v1)
  - `GROK_API_URL` (e.g., https://grok.api.server/v1)

## Startup
```bash
# (From the project root)
cd proxy
bash bin/restart.sh
```

This starts the proxy service on `127.0.0.1:8000` (HTTP only, not exposed to the public). Nginx will handle all HTTPS traffic and proxy it to this internal server.

## Production HTTPS with Nginx (Recommended)
1. Use the provided example config at `proxy/doc/nginx.conf.example` to configure Nginx as a reverse proxy.
2. Obtain SSL certificates using Let's Encrypt (see `bin/letsencrypt-certbot.sh`) or your preferred method.
3. Place your cert/key in the appropriate location (e.g., `/etc/letsencrypt/live/your.domain.com/`).
4. Reload or restart Nginx after updating certificates or config.
5. Access your service securely at `https://your.domain.com`.

**Note:** The proxy service itself does not serve HTTPS directly. All SSL/TLS is terminated at Nginx for security and scalability.

## Nginx Configuration
The `nginx.conf.example` file provides a basic configuration for Nginx to act as a reverse proxy for the proxy service. This configuration assumes that the proxy service is running on `127.0.0.1:8000` and that SSL certificates are stored in the `/etc/letsencrypt/live/your.domain.com/` directory.

## Endpoints
- `/openai/v1/chat/completions` (POST, streaming, OpenAI-compatible)
- `/grok/v1/chat/completions` (POST, streaming, Grok-compatible)

## Environment Variables
- `OPENAI_API_URL`: Base URL for OpenAI API
- `GROK_API_URL`: Base URL for Grok API

## Logs
- All logs are written to both the console and `proxy/proxy.log`.
- The log file is automatically rotated when it reaches 5MB (up to 3 backups kept).
- Logs include request paths, headers (except Authorization), client info, errors, warnings, and streaming/completion events.
- This setup is suitable for both debugging and production monitoring.

## Stopping the Service
Find the running process and kill it:
```bash
ps aux | grep 'uvicorn proxy.proxy:app'
kill <PID>
```

## Notes
- Ensure your Python virtual environment is activated if dependencies are not globally installed.
- API keys must be provided in the `Authorization` header of each request (not via environment variables).
