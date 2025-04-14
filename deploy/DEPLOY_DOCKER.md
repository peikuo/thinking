# Docker Deployment Guide for Thinking

This guide provides instructions for deploying the Thinking AI Model Comparison Platform using Docker and Docker Compose, which simplifies deployment and ensures consistency across environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Docker Configuration](#docker-configuration)
4. [Deployment Steps](#deployment-steps)
5. [Scaling and Management](#scaling-and-management)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker and Docker Compose installed on your server
- Git installed for cloning the repository
- API keys for the AI services (OpenAI, Grok, Qwen, DeepSeek)
- A domain name (optional, but recommended for production)

## Project Structure

We'll create the following Docker-related files in the project:

```
thinking/
├── docker-compose.yml       # Main Docker Compose configuration
├── .env.docker             # Environment variables for Docker
├── backend/
│   ├── Dockerfile          # Backend Docker configuration
│   └── ...
├── frontend/
│   ├── Dockerfile          # Frontend Docker configuration
│   └── ...
└── nginx/
    ├── Dockerfile          # Nginx Docker configuration
    └── nginx.conf          # Nginx configuration
```

## Docker Configuration

Let's create the necessary Docker files:

### 1. Backend Dockerfile

Create a file at `/Users/peik/Workspace/windcode/thinking/backend/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn uvicorn

# Copy application code
COPY . .

# Run the application
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
```

### 2. Frontend Dockerfile

Create a file at `/Users/peik/Workspace/windcode/thinking/frontend/Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 3. Nginx Configuration

Create a directory for Nginx configuration:

```bash
mkdir -p /Users/peik/Workspace/windcode/thinking/nginx
```

Create a file at `/Users/peik/Workspace/windcode/thinking/nginx/nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Docker Compose Configuration

Create a file at `/Users/peik/Workspace/windcode/thinking/docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Backend service
  backend:
    build: ./backend
    restart: always
    env_file:
      - .env.docker
    volumes:
      - ./backend/.config:/app/.config
    networks:
      - thinking-network

  # Frontend service
  frontend:
    build: ./frontend
    restart: always
    depends_on:
      - backend
    networks:
      - thinking-network

  # Nginx service for routing
  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./frontend/dist:/usr/share/nginx/html
      - ./data/certbot/conf:/etc/letsencrypt
      - ./data/certbot/www:/var/www/certbot
    depends_on:
      - backend
      - frontend
    networks:
      - thinking-network

  # Certbot service for SSL certificates
  certbot:
    image: certbot/certbot
    restart: unless-stopped
    volumes:
      - ./data/certbot/conf:/etc/letsencrypt
      - ./data/certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

networks:
  thinking-network:
    driver: bridge
```

### 5. Docker Environment File

Create a file at `/Users/peik/Workspace/windcode/thinking/.env.docker`:

```
# Environment
THINKING_ENV=prd

# API Keys
OPENAI_API_KEY=your_openai_api_key
GROK_API_KEY=your_grok_api_key
QWEN_API_KEY=your_qwen_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_DEBUG=false
LOG_LEVEL=info
```

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/peikuo/thinking.git
cd thinking
```

### 2. Configure Environment Variables

Edit the `.env.docker` file with your API keys and other configuration:

```bash
nano .env.docker
```

### 3. Update Frontend API Configuration

Update the API base URL in the frontend configuration:

```bash
nano frontend/src/config/api-config.ts
```

Change the `baseUrl` to:

```typescript
export const baseUrl = process.env.NODE_ENV === 'production'
  ? '/api'  // This will be proxied through Nginx
  : 'http://localhost:8000/api';
```

### 4. Build and Start the Services

```bash
docker-compose up -d
```

This command will build the Docker images and start the containers in detached mode.

### 5. Configure SSL (Optional)

If you have a domain name and want to set up SSL:

```bash
# Stop the services
docker-compose down

# Initialize SSL certificates
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot -d your-domain.com --email your-email@example.com --agree-tos --no-eff-email

# Update Nginx configuration for SSL
nano nginx/nginx.conf
```

Add SSL configuration to `nginx/nginx.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Frontend
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Restart the services:

```bash
docker-compose up -d
```

## Scaling and Management

### Viewing Logs

```bash
# View logs for all services
docker-compose logs

# View logs for a specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx

# Follow logs in real-time
docker-compose logs -f
```

### Scaling Services

To scale the backend service for handling more traffic:

```bash
docker-compose up -d --scale backend=3
```

Note: When scaling the backend, you'll need to update the Nginx configuration to use load balancing.

### Updating the Application

To update the application with new changes:

```bash
# Pull the latest changes
git pull

# Rebuild and restart the services
docker-compose up -d --build
```

### Stopping the Services

```bash
docker-compose down
```

## Troubleshooting

### Container Issues

If containers are not starting properly:

```bash
# Check container status
docker-compose ps

# View detailed container logs
docker-compose logs -f service_name
```

### Network Issues

If services can't communicate with each other:

```bash
# Check the network
docker network ls
docker network inspect thinking_thinking-network
```

### Database Persistence (If Added Later)

If you add a database to the project:

```bash
# Add a volume for database persistence
volumes:
  db-data:
    driver: local
```

Update the docker-compose.yml to include the database service and volume.

### Backup and Restore

To backup Docker volumes and configurations:

```bash
# Create a backup directory
mkdir -p backups

# Backup volumes
docker run --rm -v thinking_db-data:/source -v $(pwd)/backups:/backup alpine tar -czf /backup/db-data-$(date +%Y%m%d).tar.gz -C /source .

# Backup configuration files
tar -czf backups/config-$(date +%Y%m%d).tar.gz .env.docker nginx/nginx.conf
```

To restore from backups:

```bash
# Restore volumes
docker run --rm -v thinking_db-data:/target -v $(pwd)/backups:/backup alpine sh -c "tar -xzf /backup/db-data-YYYYMMDD.tar.gz -C /target"

# Restore configuration files
tar -xzf backups/config-YYYYMMDD.tar.gz
```

## Security Considerations

1. **Environment Variables**:
   - Never commit `.env.docker` to version control
   - Consider using Docker secrets for sensitive information in production

2. **Network Security**:
   - Use the internal Docker network for service-to-service communication
   - Only expose necessary ports to the host

3. **Regular Updates**:
   - Keep Docker images updated
   - Regularly update the application code

4. **Resource Limits**:
   - Set resource limits for containers to prevent resource exhaustion:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '0.5'
             memory: 512M
   ```

## Conclusion

This Docker-based deployment approach provides a consistent, scalable, and maintainable way to deploy the Thinking AI Model Comparison Platform. It simplifies the deployment process and makes it easier to manage the application in production.

For additional assistance or troubleshooting, refer to the Docker and Docker Compose documentation or reach out to your system administrator.
