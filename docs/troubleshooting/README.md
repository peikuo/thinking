# Troubleshooting Guide for Thinking Platform

This guide provides solutions for common issues you might encounter when deploying or running the Thinking platform.

## HTTP 500 Errors

If you're experiencing HTTP 500 errors after deployment, follow these troubleshooting steps:

### 1. Check Backend Service Logs

```bash
# Check the systemd service logs
journalctl -u thinking-backend.service -n 100 --no-pager
```

Look for error messages that might indicate what's causing the issue.

### 2. Check Nginx Error Logs

```bash
# On Ubuntu/Debian
vi /var/log/nginx/error.log

# On Alibaba Cloud Linux
vi /var/log/nginx/error.log
```

### 3. Verify Environment Variables and API Keys

Make sure all required environment variables are correctly set in your `.env` file:

```bash
# View the current .env file
vi /path/to/thinking/backend/.env
```

Ensure that all API keys are valid and correctly formatted.

### 4. Test API Endpoints Directly

Test the backend API endpoints directly to isolate frontend vs. backend issues:

```bash
# Test the health endpoint
curl http://localhost:8000/api/health

# Test a specific model endpoint (replace with your actual API key)
curl -X POST http://localhost:8000/api/chat/openai \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

### 5. Check File Permissions and Ownership

Ensure the application files have the correct permissions:

```bash
# Set appropriate ownership
sudo chown -R your_user:your_group /path/to/thinking

# Set appropriate permissions
sudo chmod -R 755 /path/to/thinking
```

### 6. Verify Python Dependencies

Make sure all required Python packages are installed:

```bash
# Activate the virtual environment
source /path/to/thinking/backend/venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Common Deployment Issues

### SSL Certificate Problems

If you're having issues with SSL certificates:

1. Check that Certbot successfully generated certificates:
   ```bash
   ls -la /etc/letsencrypt/live/your-domain.com/
   ```

2. Verify Nginx configuration is correctly referencing the certificates:
   ```bash
   vi /etc/nginx/conf.d/thinking.conf
   ```

3. Test Nginx configuration:
   ```bash
   sudo nginx -t
   ```

### Frontend Connection Issues

If the frontend cannot connect to the backend:

1. Check that the API URLs in the frontend configuration are correct:
   ```bash
   vi /path/to/thinking/frontend/src/config/api-config.ts
   ```

2. Verify that CORS is properly configured in the backend:
   ```bash
   vi /path/to/thinking/backend/main.py
   ```

3. Check browser console for network errors

## Rollback Procedures

If you need to rollback to a previous version after an unsuccessful upgrade:

1. Checkout the previous working commit:
   ```bash
   cd /path/to/thinking
   git log  # Find the previous commit hash
   git checkout <previous-commit-hash>
   ```

2. Rebuild and restart services:
   ```bash
   # Rebuild frontend
   cd frontend
   npm install
   npm run build

   # Restart backend service
   sudo systemctl restart thinking-backend.service

   # Restart Nginx
   sudo systemctl restart nginx
   ```

## Getting Additional Help

If you're still experiencing issues after following these troubleshooting steps, please:

1. Gather relevant logs and error messages
2. Create a detailed description of the issue
3. Open an issue on the project's GitHub repository with this information
