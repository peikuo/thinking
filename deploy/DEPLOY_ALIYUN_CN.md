# 在阿里云上部署 Thinking

本指南提供了在运行 Linux 的阿里云 ECS（弹性计算服务）实例上部署 Thinking AI 模型比较平台的详细步骤。

## 目录

1. [前提条件](#前提条件)
2. [设置阿里云 ECS 实例](#设置阿里云-ecs-实例)
3. [服务器准备](#服务器准备)
4. [部署后端](#部署后端)
5. [部署前端](#部署前端)
6. [设置 Nginx](#设置-nginx)
7. [配置 SSL](#配置-ssl)
8. [设置 Systemd 服务](#设置-systemd-服务)
9. [监控和维护](#监控和维护)
10. [故障排除](#故障排除)

## 前提条件

- 具有 ECS 访问权限的阿里云账户
- 域名（可选，但生产环境推荐使用）
- AI 服务的 API 密钥（OpenAI、Grok、Qwen、DeepSeek）
- 基本熟悉 Linux 命令和 SSH

## 设置阿里云 ECS 实例

1. **登录阿里云控制台**：
   - 访问[阿里云控制台](https://account.aliyun.com/login/login.htm)
   - 导航至 ECS 服务

2. **创建 ECS 实例**：
   - 点击"创建实例"
   - 选择地区（最好靠近目标用户）
   - 选择实例类型：
     - 推荐：生产环境至少 2 vCPU 和 4GB RAM
     - 开发/测试环境：1 vCPU 和 2GB RAM 可能足够
   - 选择 Linux 发行版：
     - 推荐：Ubuntu 22.04 LTS 或阿里云 Linux 3
   - 配置存储：
     - 系统盘：至少 40GB
     - 数据盘：可选，根据需求配置
   - 配置网络：
     - 创建新的 VPC 或使用现有的
     - 配置安全组，允许以下端口：
       - HTTP (80)
       - HTTPS (443)
       - SSH (22)
   - 配置实例详情：
     - 设置强密码或使用 SSH 密钥（推荐）
   - 检查并创建实例

3. **连接到实例**：
   ```bash
   ssh root@<实例IP地址>
   # 或者如果使用 SSH 密钥
   ssh -i /path/to/your/key.pem root@<实例IP地址>
   ```

## 服务器准备

1. **更新系统**：
   ```bash
   apt update && apt upgrade -y
   # 或者对于阿里云 Linux/CentOS
   yum update -y
   ```

2. **安装必要软件包**：
   ```bash
   # 对于 Ubuntu/Debian
   apt install -y git python3 python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx

   # 对于阿里云 Linux/CentOS
   yum install -y git python3 python3-pip nodejs npm nginx certbot python3-certbot-nginx
   ```

3. **安装 Node.js 和 npm**（如果未包含或版本过旧）：
   ```bash
   # 安装 Node.js 18.x（或更新版本）
   curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
   apt install -y nodejs
   # 或者对于阿里云 Linux/CentOS
   curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
   yum install -y nodejs
   ```

4. **创建非 root 用户**（可选但推荐）：
   ```bash
   adduser thinking
   usermod -aG sudo thinking  # 对于 Ubuntu/Debian
   # 或者对于阿里云 Linux/CentOS
   usermod -aG wheel thinking
   
   # 切换到新用户
   su - thinking
   ```

## 部署后端

1. **克隆仓库**：
   ```bash
   git clone https://github.com/peikuo/thinking.git
   cd thinking
   ```

2. **设置后端**：
   ```bash
   cd backend
   
   # 创建并激活虚拟环境
   python3 -m venv venv
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   ```

3. **配置环境变量**：
   ```bash
   # 创建 .env 文件
   cp .env.example .env
   
   # 编辑 .env 文件，添加 API 密钥和设置
   nano .env
   ```

   在 `.env` 文件中更新以下变量：
   ```
   # 环境
   THINKING_ENV=prd  # 使用生产环境
   
   # API 密钥
   OPENAI_API_KEY=your_openai_api_key
   GROK_API_KEY=your_grok_api_key
   QWEN_API_KEY=your_qwen_api_key
   DEEPSEEK_API_KEY=your_deepseek_api_key
   
   # 服务器配置
   SERVER_HOST=0.0.0.0  # 监听所有接口
   SERVER_PORT=8000
   SERVER_DEBUG=false  # 在生产环境中禁用调试
   LOG_LEVEL=info
   ```

4. **测试后端**：
   ```bash
   # 临时启动服务器进行测试
   uvicorn main:app --host 0.0.0.0 --port 8000
   
   # 测试后按 Ctrl+C 停止
   ```

## 部署前端

1. **导航到前端目录**：
   ```bash
   cd ../frontend
   ```

2. **安装依赖**：
   ```bash
   npm install
   ```

3. **配置前端**：
   更新 `src/config/api-config.ts` 中的 API 端点，指向您的后端：
   ```bash
   nano src/config/api-config.ts
   ```
   
   修改端点以使用您的后端 API：
   ```typescript
   const apiConfig: ApiConfig = {
     endpoints: {
       openai: "https://your-domain.com/api/chat/openai",  // 替换为您的域名
       grok: "https://your-domain.com/api/chat/grok",     // 替换为您的域名
       qwen: "https://your-domain.com/api/chat/qwen",     // 替换为您的域名
       deepseek: "https://your-domain.com/api/chat/deepseek" // 替换为您的域名
     },
     timeouts: {
       default: 30000 // 30秒
     }
   };
   ```
   
   对于本地开发，您可以使用：
   ```typescript
   const apiConfig: ApiConfig = {
     endpoints: {
       openai: "http://localhost:8000/api/chat/openai",
       grok: "http://localhost:8000/api/chat/grok",
       qwen: "http://localhost:8000/api/chat/qwen",
       deepseek: "http://localhost:8000/api/chat/deepseek"
     },
     timeouts: {
       default: 30000 // 30秒
     }
   };
   ```

4. **构建前端**：
   ```bash
   npm run build
   ```
   
   这将创建一个包含生产构建的 `dist` 目录。

## 设置 Nginx

1. **创建 Nginx 配置文件**：
   对于 Ubuntu/Debian：
   ```bash
   sudo vi /etc/nginx/sites-available/thinking
   ```
   对于阿里云 Linux：
   ```bash
   sudo mkdir -p /etc/nginx/conf.d
   sudo vi /etc/nginx/conf.d/thinking.conf
   ```

2. **添加以下配置**：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;  # 替换为您的域名或 IP
       
       # 前端
       location / {
           root /home/thinking/thinking/frontend/dist;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
       
       # 后端 API
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

3. **启用站点**：
   对于 Ubuntu/Debian：
   ```bash
   sudo ln -s /etc/nginx/sites-available/thinking /etc/nginx/sites-enabled/
   sudo nginx -t  # 测试配置
   sudo systemctl restart nginx
   ```
   对于阿里云 Linux：
   ```bash
   sudo nginx -t  # 测试配置
   sudo systemctl restart nginx
   ```

## 配置 SSL

1. **安装 Certbot**（如果尚未安装）：
   对于 Ubuntu/Debian：
   ```bash
   sudo apt update
   sudo apt install -y certbot python3-certbot-nginx
   ```
   
   对于阿里云 Linux：
   ```bash
   sudo yum install -y epel-release
   sudo yum install -y certbot python3-certbot-nginx
   ```

2. **使用 Certbot 设置 SSL**（如果您有域名）：
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```
   
   按照提示完成 SSL 设置。

3. **域名验证问题解决**：
   如果您在使用 Nginx 自动验证时遇到问题，可以使用 DNS 验证方式：
   ```bash
   sudo certbot certonly --manual --preferred-challenges dns -d your-domain.com
   ```
   
   按照指示在您的 DNS 提供商创建 TXT 记录。对于 GoDaddy：
   - 登录您的 GoDaddy 账户
   - 进入您域名的 DNS 管理
   - 添加一个主机名为 `_acme-challenge` 的 TXT 记录，值为 Certbot 提供的字符串
   - 等待 10-30 分钟让 DNS 变更生效
   - 使用 `dig _acme-challenge.your-domain.com TXT` 验证
   - 继续 Certbot 过程

4. **仅使用 IP 的部署**：
   如果您只使用 IP 地址而没有域名，生成自签名证书：
   ```bash
   sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt
   ```

5. **配置 Nginx 使用 SSL**：
   更新您的 Nginx 配置以使用 SSL 证书：
   ```bash
   sudo vi /etc/nginx/conf.d/thinking.conf
   ```
   
   对于 Let's Encrypt 证书：
   ```nginx
   # HTTP 服务器 - 重定向到 HTTPS
   server {
       listen 80;
       listen [::]:80;
       server_name your-domain.com your-ip-address _;
       
       # 将所有 HTTP 请求重定向到 HTTPS
       return 301 https://$host$request_uri;
   }

   # HTTPS 服务器
   server {
       listen 443 ssl;
       listen [::]:443 ssl;
       server_name your-domain.com your-ip-address _;
       
       # SSL 配置使用 Let's Encrypt 证书
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_prefer_server_ciphers on;
       ssl_ciphers EECDH+AESGCM:EDH+AESGCM;
       ssl_session_cache shared:SSL:10m;
       ssl_session_timeout 180m;
       
       # 前端
       location / {
           root /home/thinking/thinking/frontend/dist;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
       
       # 后端 API
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
       
       # Let's Encrypt 的 ACME 验证路径
       location ~ /.well-known/acme-challenge {
           allow all;
           root /var/www/html;
       }
   }
   ```
   
   对于自签名证书，将 SSL 配置部分替换为：
   ```nginx
   # 使用自签名证书的 SSL 配置
   ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
   ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
   ```

6. **设置自动证书更新**：
   ```bash
   sudo crontab -e
   ```
   
   添加以下行每天运行两次更新检查：
   ```
   0 0,12 * * * certbot renew --quiet
   ```

## 设置 Systemd 服务

1. **为后端创建 Systemd 服务文件**：
   ```bash
   sudo vi /etc/systemd/system/thinking-backend.service
   ```

2. **添加以下配置**：
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

3. **启用并启动服务**：
   ```bash
   sudo systemctl enable thinking-backend
   sudo systemctl start thinking-backend
   sudo systemctl status thinking-backend  # 检查状态
   ```

## 项目升级

1. **拉取最新变更**：
   ```bash
   # 切换到 thinking 用户
   sudo su - thinking
   
   # 导航到项目目录
   cd ~/thinking
   
   # 拉取最新变更
   git pull origin main
   ```

2. **更新后端**：
   ```bash
   # 导航到后端目录
   cd ~/thinking/backend
   
   # 激活虚拟环境
   source venv/bin/activate
   
   # 安装新的依赖
   pip install -r requirements.txt
   
   # 重启后端服务
   sudo systemctl restart thinking-backend
   ```

3. **重建前端**：
   ```bash
   # 导航到前端目录
   cd ~/thinking/frontend
   
   # 安装新的依赖
   npm install
   
   # 构建前端
   npm run build
   ```

4. **检查配置变更**：
   ```bash
   # 检查是否有配置文件的变更
   cd ~/thinking
   git diff --name-only HEAD@{1} HEAD | grep -E '\.env\.example|\.config'
   ```
   
   如果配置文件有变更，请相应地更新您的配置。

5. **验证升级**：
   ```bash
   # 检查后端服务状态
   sudo systemctl status thinking-backend
   
   # 检查日志是否有错误
   sudo journalctl -u thinking-backend -n 50
   ```

6. **必要时回滚**：
   ```bash
   # 如果需要回滚到之前的版本
   cd ~/thinking
   git log --oneline  # 找到要回滚到的提交哈希
   git reset --hard <commit-hash>
   
   # 然后按照步骤 2-4 更新后端和前端
   ```

## 监控和维护

1. **设置基本监控**：
   ```bash
   # 安装监控工具
   sudo apt install -y htop glances
   ```

2. **查看日志**：
   ```bash
   # 后端日志
   sudo journalctl -u thinking-backend -f
   
   # Nginx 日志
   sudo tail -f /var/log/nginx/access.log
   sudo tail -f /var/log/nginx/error.log
   ```

3. **自动更新**（可选）：
   ```bash
   # 安装 unattended-upgrades 进行安全更新
   sudo apt install -y unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

## 故障排除

### 后端问题

1. **检查后端是否运行**：
   ```bash
   sudo systemctl status thinking-backend
   ```

2. **验证 API 连接**：
   ```bash
   curl http://localhost:8000/api/health
   ```

3. **检查日志中的错误**：
   ```bash
   sudo journalctl -u thinking-backend -n 100
   ```

### 前端问题

1. **验证 Nginx 配置**：
   ```bash
   sudo nginx -t
   ```

2. **检查静态文件是否被服务**：
   ```bash
   ls -la /home/thinking/thinking/frontend/dist
   ```

3. **检查 Nginx 日志**：
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

### 网络问题

1. **检查防火墙设置**：
   ```bash
   # 对于 Ubuntu/Debian
   sudo ufw status
   
   # 对于阿里云 Linux/CentOS
   sudo firewall-cmd --list-all
   ```

2. **验证阿里云安全组规则**：
   - 进入阿里云控制台
   - 导航至 ECS > 实例 > 安全组
   - 确保允许端口 80、443 和 22

## 备份策略

1. **数据库备份**（如果将来添加数据库）：
   ```bash
   # PostgreSQL 示例
   pg_dump -U username -d database_name > backup.sql
   ```

2. **配置备份**：
   ```bash
   # 备份环境变量
   cp /home/thinking/thinking/backend/.env /home/thinking/backups/env_backup_$(date +%Y%m%d)
   
   # 备份 Nginx 配置
   sudo cp /etc/nginx/sites-available/thinking /home/thinking/backups/nginx_config_$(date +%Y%m%d)
   ```

3. **使用 Cron 自动备份**：
   ```bash
   crontab -e
   ```
   
   添加如下行：
   ```
   0 2 * * * tar -czf /home/thinking/backups/thinking_backup_$(date +\%Y\%m\%d).tar.gz /home/thinking/thinking
   ```

## 扩展考虑

对于更高流量场景：

1. **水平扩展**：
   - 部署多个 ECS 实例
   - 使用负载均衡服务（SLB）分配流量

2. **垂直扩展**：
   - 将 ECS 实例升级到更高规格

3. **数据库扩展**（如果稍后添加）：
   - 考虑使用云数据库 RDS 而不是本地数据库

4. **CDN 集成**：
   - 使用阿里云 CDN 提供静态前端资源

## 安全最佳实践

1. **保持系统更新**：
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **安全 SSH**：
   - 禁用密码认证
   - 仅使用 SSH 密钥
   - 更改默认 SSH 端口

3. **设置 Fail2Ban**：
   ```bash
   sudo apt install -y fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

4. **定期安全审计**：
   - 检查日志中的可疑活动
   - 检查未授权访问尝试

---

本部署指南应该能帮助您在阿里云上设置 Thinking AI 模型比较平台。如需其他帮助或故障排除，请参阅阿里云文档或联系您的系统管理员。
