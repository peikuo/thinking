# Deploying Thinking on Aliyun Cloud

This guide provides step-by-step instructions for deploying the Thinking AI Model Comparison Platform on Aliyun Cloud using ECS (Elastic Compute Service) instances running Linux.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setting Up Aliyun ECS Instance](#setting-up-aliyun-ecs-instance)
3. [Server Preparation](#server-preparation)
4. [Deploying the Backend](#deploying-the-backend)
5. [Deploying the Frontend](#deploying-the-frontend)
6. [Setting Up Nginx](#setting-up-nginx)
7. [Configuring SSL](#configuring-ssl)
8. [Setting Up Systemd Services](#setting-up-systemd-services)
9. [Monitoring and Maintenance](#monitoring-and-maintenance)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

- An Aliyun account with access to ECS
- A domain name (optional, but recommended for production)
- API keys for the AI services (OpenAI, Grok, Qwen, DeepSeek)
- Basic familiarity with Linux commands and SSH

## Setting Up Aliyun ECS Instance

1. **Log in to the Aliyun Console**:
   - Go to the [Aliyun Console](https://account.aliyun.com/login/login.htm)
   - Navigate to the ECS service

2. **Create an ECS Instance**:
   - Click "Create Instance"
   - Select a region (preferably close to your target users)
   - Choose an instance type:
     - Recommended: At least 2 vCPUs and 4GB RAM for production
     - For development/testing: 1 vCPU and 2GB RAM may be sufficient
   - Select a Linux distribution:
     - Recommended: Ubuntu 22.04 LTS or Alibaba Cloud Linux 3
   - Configure storage:
     - System disk: At least 40GB
     - Data disk: Optional, based on your needs
   - Configure network:
     - Create a new VPC or use an existing one
     - Configure security groups to allow:
       - HTTP (80)
       - HTTPS (443)
       - SSH (22)
   - Configure instance details:
     - Set a strong root password or use SSH key (recommended)
   - Review and create the instance

3. **Connect to Your Instance**:
   ```bash
   ssh root@<your-instance-ip>
   # Or if using an SSH key
   ssh -i /path/to/your/key.pem root@<your-instance-ip>
   ```

## Server Preparation

1. **Update the System**:
   ```bash
   apt update && apt upgrade -y
   # Or for Alibaba Cloud Linux/CentOS
   yum update -y
   ```

2. **Install Required Packages**:
   ```bash
   # For Ubuntu/Debian
   apt install -y git python3 python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx

   # For Alibaba Cloud Linux/CentOS
   yum install -y git python3 python3-pip nodejs npm nginx certbot python3-certbot-nginx
   ```

3. **Install Node.js and npm** (if not included or outdated):
   ```bash
   # Install Node.js 18.x (or newer)
   curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
   apt install -y nodejs
   # Or for Alibaba Cloud Linux/CentOS
   curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
   yum install -y nodejs
   ```

4. **Create a Non-Root User** (optional but recommended):
   ```bash
   adduser thinking
   usermod -aG sudo thinking  # For Ubuntu/Debian
   # Or for Alibaba Cloud Linux/CentOS
   usermod -aG wheel thinking
   
   # Switch to the new user
   su - thinking
   ```

## Deploying the Backend

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/peikuo/thinking.git
   cd thinking
   ```

2. **Set Up the Backend**:
   ```bash
   cd backend
   
   # Create and activate a virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit the .env file with your API keys and settings
   nano .env
   ```

   Update the following variables in your `.env` file:
   ```
   # Environment
   THINKING_ENV=prd  # Use production environment
   
   # API Keys
   OPENAI_API_KEY=your_openai_api_key
   GROK_API_KEY=your_grok_api_key
   QWEN_API_KEY=your_qwen_api_key
   DEEPSEEK_API_KEY=your_deepseek_api_key
   
   # GLM API Configuration (primarily for Chinese language)
   GLM_API_KEY=your_glm_api_key
   GLM_API_URL=https://open.bigmodel.cn/api/paas/v4
   GLM_MODEL=glm-4
   
   # Doubao API Configuration (primarily for Chinese language)
   DOUBAO_API_KEY=your_doubao_api_key
   DOUBAO_API_URL=https://ark.cn-beijing.volces.com/api/v3
   DOUBAO_MODEL=doubao-1-5-pro-32k-250115
   
   # Other API URLs
   OPENAI_API_URL=https://api.openai.com/v1
   GROK_API_URL=https://api.grok.com/v1
   QWEN_API_URL=https://api.qwen.com/v1
   DEEPSEEK_API_URL=https://api.deepseek.com/v1
   
   # Server Configuration
   SERVER_HOST=0.0.0.0  # Listen on all interfaces
   SERVER_PORT=8000
   SERVER_DEBUG=false  # Disable debug in production
   LOG_LEVEL=info
   ```

4. **Test the Backend**:
   ```bash
   # Start the server temporarily to test
   uvicorn main:app --host 0.0.0.0 --port 8000
   
   # Press Ctrl+C to stop after testing
   ```

## Deploying the Frontend

1. **Navigate to the Frontend Directory**:
   ```bash
   cd ../frontend
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Configure the Frontend**:
   Update the API endpoints in `src/config/api-config.ts` to point to your backend:
   ```bash
   nano src/config/api-config.ts
   ```
   
   Modify the endpoints to use your backend API:
   ```typescript
   const apiConfig: ApiConfig = {
     endpoints: {
       openai: "http://localhost:8000/api/chat/openai",    // Replace with your domain
       grok: "http://localhost:8000/api/chat/grok",       // Replace with your domain
       qwen: "http://localhost:8000/api/chat/qwen",       // Replace with your domain
       deepseek: "http://localhost:8000/api/chat/deepseek", // Replace with your domain
       doubao: "http://localhost:8000/api/chat/doubao",   // Replace with your domain (Chinese locale)
       glm: "http://localhost:8000/api/chat/glm"          // Replace with your domain (Chinese locale)
     },
     timeouts: {
       default: 30000 // 30 seconds
     }
   };
   ```
   
   For local development, you can use:
   ```typescript
   const apiConfig: ApiConfig = {
     endpoints: {
       openai: "http://localhost:8000/api/chat/openai",
       grok: "http://localhost:8000/api/chat/grok",
       doubao: "http://localhost:8000/api/chat/doubao",
       glm: "http://localhost:8000/api/chat/glm",
       qwen: "http://localhost:8000/api/chat/qwen",
       deepseek: "http://localhost:8000/api/chat/deepseek"
     },
     timeouts: {
       default: 30000 // 30 seconds
     }
   };
   ```

4. **Build the Frontend**:
   ```bash
   npm run build
   ```
   
   This will create a `dist` directory with the production build.

## Setting Up Nginx

1. **Create an Nginx Configuration File**:
   For Ubuntu/Debian:
   ```bash
   sudo nano /etc/nginx/sites-available/thinking
   ```
   For Alibaba Cloud Linux:
   ```bash
   sudo mkdir -p /etc/nginx/conf.d
   sudo vi /etc/nginx/conf.d/thinking.conf
   ```

2. **Add the Following Configuration**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;  # Replace with your domain or IP
       
       # Frontend
       location / {
           root /home/thinking/thinking/frontend/dist;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
       
       # Backend API
       location /api/ {
           proxy_pass http://localhost:8000/;
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

3. **Enable the Site**:
   For Ubuntu/Debian:
   ```bash
   sudo ln -s /etc/nginx/sites-available/thinking /etc/nginx/sites-enabled/
   sudo nginx -t  # Test the configuration
   sudo systemctl restart nginx
   ```
   For Alibaba Cloud Linux:
   ```bash
   sudo nginx -t  # Test the configuration
   sudo systemctl restart nginx
   ```

## Configuring SSL

1. **Install Certbot** (if not already installed):
   For Ubuntu/Debian:
   ```bash
   sudo apt update
   sudo apt install -y certbot python3-certbot-nginx
   ```
   
   For Alibaba Cloud Linux:
   ```bash
   sudo yum install -y epel-release
   sudo yum install -y certbot python3-certbot-nginx
   ```

2. **Set Up SSL with Certbot** (if you have a domain):
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```
   
   Follow the prompts to complete the SSL setup.

3. **For Domain Verification Issues**:
   If you're having trouble with the automatic Nginx verification, you can use the DNS challenge method:
   ```bash
   sudo certbot certonly --manual --preferred-challenges dns -d your-domain.com
   ```
   
   Follow the instructions to create a TXT record at your DNS provider. For GoDaddy:
   - Log in to your GoDaddy account
   - Go to the DNS management for your domain
   - Add a TXT record with host `_acme-challenge` and the value provided by Certbot
   - Wait 10-30 minutes for DNS propagation
   - Verify with `dig _acme-challenge.your-domain.com TXT`
   - Continue with the Certbot process

4. **For IP-Only Deployments**:
   If you're using only an IP address without a domain, generate a self-signed certificate:
   ```bash
   sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt
   ```

5. **Configure Nginx for SSL**:
   Update your Nginx configuration to use SSL certificates:
   ```bash
   sudo vi /etc/nginx/conf.d/thinking.conf
   ```
   
   For Let's Encrypt certificates:
   ```nginx
   # HTTP server - redirects to HTTPS
   server {
       listen 80;
       listen [::]:80;
       server_name your-domain.com your-ip-address _;
       
       # Redirect all HTTP requests to HTTPS
       return 301 https://$host$request_uri;
   }

   # HTTPS server
   server {
       listen 443 ssl;
       listen [::]:443 ssl;
       server_name your-domain.com your-ip-address _;
       
       # SSL configuration with Let's Encrypt certificates
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_prefer_server_ciphers on;
       ssl_ciphers EECDH+AESGCM:EDH+AESGCM;
       ssl_session_cache shared:SSL:10m;
       ssl_session_timeout 180m;
       
       # Frontend
       location / {
           root /home/thinking/thinking/frontend/dist;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
       
       # Backend API
       location /api/ {
           proxy_pass http://localhost:8000/;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       # ACME challenge location for Let's Encrypt renewals
       location ~ /.well-known/acme-challenge {
           allow all;
           root /var/www/html;
       }
   }
   ```
   
   For self-signed certificates, replace the SSL configuration section with:
   ```nginx
   # SSL configuration with self-signed certificates
   ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
   ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
   ```

6. **Set Up Automatic Certificate Renewal**:
   ```bash
   sudo crontab -e
   ```
   
   Add this line to run the renewal check twice daily:
   ```
   0 0,12 * * * certbot renew --quiet
   ```

## Language-Specific Model Selection

The Thinking platform now supports language-specific model selection, which automatically selects different AI models based on the user's language setting:

- **Chinese Locale (zh)**:
  - Default models: DeepSeek, Qwen, Doubao, GLM
  - Summary generation uses these models

- **English Locale (en)**:
  - Default models: OpenAI, Grok, Qwen, DeepSeek
  - Summary generation uses these models

This selection happens automatically based on the language setting in the user's browser or their explicit language selection in the UI.

### HTML Content Rendering

The platform now properly renders HTML tags in model responses. This is particularly important for table cells that contain formatted content like lists with `<br>` tags.

## Setting Up Systemd Services

1. **Create a Systemd Service File for the Backend**:
   ```bash
   sudo vi /etc/systemd/system/thinking-backend.service
   ```

2. **Add the Following Configuration**:
   ```ini
   [Unit]
   Description=Thinking AI Platform Backend
   After=network.target
   
   [Service]
   User=thinking
   Group=thinking
   WorkingDirectory=/home/thinking/thinking/backend
   Environment="PATH=/home/thinking/thinking/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
   Environment="PYTHONPATH=/home/thinking/thinking/backend"
   ExecStart=/home/thinking/thinking/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start the Service**:
   ```bash
   sudo systemctl enable thinking-backend
   sudo systemctl start thinking-backend
   sudo systemctl status thinking-backend  # Check status
   ```

## Upgrading the Project

1. **Pull Latest Changes**:
   ```bash
   # Switch to the thinking user
   sudo su - thinking
   
   # Navigate to the project directory
   cd ~/thinking
   
   # Pull the latest changes
   git pull origin main
   ```

2. **Update Backend**:
   ```bash
   # Navigate to the backend directory
   cd ~/thinking/backend
   
   # Activate the virtual environment
   source venv/bin/activate
   
   # Install any new dependencies
   pip install -r requirements.txt
   
   # Restart the backend service
   sudo systemctl restart thinking-backend
   ```

3. **Rebuild Frontend**:
   ```bash
   # Navigate to the frontend directory
   cd ~/thinking/frontend
   
   # Install any new dependencies
   npm install
   
   # Build the frontend
   npm run build
   ```

4. **Check for Configuration Changes**:
   ```bash
   # Check if there are any changes to the configuration files
   cd ~/thinking
   git diff --name-only HEAD@{1} HEAD | grep -E '\.env\.example|\.config'
   ```
   
   If there are changes to configuration files, update your configuration accordingly.

5. **Verify the Upgrade**:
   ```bash
   # Check backend service status
   sudo systemctl status thinking-backend
   
   # Check logs for any errors
   sudo journalctl -u thinking-backend -n 50
   ```

6. **Rollback if Necessary**:
   ```bash
   # If you need to rollback to a previous version
   cd ~/thinking
   git log --oneline  # Find the commit hash to rollback to
   git reset --hard <commit-hash>
   
   # Then follow steps 2-4 to update the backend and frontend
   ```

## Monitoring and Maintenance

1. **Set Up Basic Monitoring**:
   ```bash
   # Install monitoring tools
   sudo apt install -y htop glances
   ```

2. **View Logs**:
   ```bash
   # Backend logs
   sudo journalctl -u thinking-backend -f
   
   # Nginx logs
   sudo tail -f /var/log/nginx/access.log
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Automatic Updates** (optional):
   ```bash
   # Install unattended-upgrades for security updates
   sudo apt install -y unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

## Troubleshooting

### Backend Issues

1. **Check if the Backend is Running**:
   ```bash
   sudo systemctl status thinking-backend
   ```

2. **Verify API Connectivity**:
   ```bash
   curl http://localhost:8000/api/health
   ```

3. **Check Logs for Errors**:
   ```bash
   sudo journalctl -u thinking-backend -n 100
   ```

### Frontend Issues

1. **Verify Nginx Configuration**:
   ```bash
   sudo nginx -t
   ```

2. **Check if Static Files are Being Served**:
   ```bash
   ls -la /home/thinking/thinking/frontend/dist
   ```

3. **Check Nginx Logs**:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

### Network Issues

1. **Check Firewall Settings**:
   ```bash
   # For Ubuntu/Debian
   sudo ufw status
   
   # For Alibaba Cloud Linux/CentOS
   sudo firewall-cmd --list-all
   ```

2. **Verify Aliyun Security Group Rules**:
   - Go to the Aliyun Console
   - Navigate to ECS > Instances > Security Groups
   - Ensure ports 80, 443, and 22 are allowed

## Backup Strategy

1. **Database Backups** (if you add a database in the future):
   ```bash
   # Example for PostgreSQL
   pg_dump -U username -d database_name > backup.sql
   ```

2. **Configuration Backups**:
   ```bash
   # Back up environment variables
   cp /home/thinking/thinking/backend/.env /home/thinking/backups/env_backup_$(date +%Y%m%d)
   
   # Back up Nginx configuration
   sudo cp /etc/nginx/sites-available/thinking /home/thinking/backups/nginx_config_$(date +%Y%m%d)
   ```

3. **Automated Backups with Cron**:
   ```bash
   crontab -e
   ```
   
   Add a line like:
   ```
   0 2 * * * tar -czf /home/thinking/backups/thinking_backup_$(date +\%Y\%m\%d).tar.gz /home/thinking/thinking
   ```

## Scaling Considerations

For higher traffic scenarios:

1. **Horizontal Scaling**:
   - Deploy multiple ECS instances
   - Use Server Load Balancer (SLB) to distribute traffic

2. **Vertical Scaling**:
   - Upgrade your ECS instance to a higher specification

3. **Database Scaling** (if added later):
   - Consider using ApsaraDB RDS instead of a local database

4. **CDN Integration**:
   - Use Alibaba Cloud CDN to serve static frontend assets

## Security Best Practices

1. **Keep Systems Updated**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Secure SSH**:
   - Disable password authentication
   - Use SSH keys only
   - Change the default SSH port

3. **Set Up Fail2Ban**:
   ```bash
   sudo apt install -y fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

4. **Regular Security Audits**:
   - Review logs for suspicious activities
   - Check for unauthorized access attempts

---

This deployment guide should help you set up the Thinking AI Model Comparison Platform on Aliyun Cloud. For additional assistance or troubleshooting, refer to the Aliyun documentation or reach out to your system administrator.
