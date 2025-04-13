# Thinking Website Deployment Guide

This guide explains how to deploy both the frontend and backend components of the Thinking Website application to different environments. Last updated: April 7, 2025.

## Recent Updates

### Frontend
- Added markdown rendering for AI responses using `react-markdown` and `remark-gfm`
- Enhanced loading animations with custom wave effects and model-specific styling
- Added support for language localization in the UI

### Backend
- Added language localization support for AI response summaries
- Updated API endpoints to accept language parameters
- Improved response formatting for markdown compatibility

# Backend Deployment Guide

This guide explains how to deploy the Thinking Website backend to different environments.

## Prerequisites

- Python 3.9+ installed
- Access to API keys for:
  - OpenAI
  - Groq
  - Qwen
  - DeepSeek
- Git access to the repository

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/thinking.git
   cd thinking/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   - The application uses environment-specific configuration files in the `config/` directory
   - For development, edit `config/config_dev.json` with your API keys

5. Start the development server:
   ```bash
   python main.py dev
   ```

## Environment-Specific Deployment

The backend supports three environments:
- `dev`: Development environment
- `test`: Testing environment
- `prd`: Production environment

### Configuration Files

Each environment has its own configuration file:
- `config/config_dev.json`
- `config/config_test.json`
- `config/config_prd.json`

Ensure each file has the correct settings for its environment, particularly:
- API keys
- Model selections
- Server configuration

### Deploying to Test Environment

1. Update the test configuration:
   ```bash
   # Edit config/config_test.json with appropriate settings
   ```

2. Start the server in test mode:
   ```bash
   python main.py test
   ```

### Deploying to Production

1. Update the production configuration:
   ```bash
   # Edit config/config_prd.json with production API keys and settings
   ```

2. Start the server in production mode:
   ```bash
   python main.py prd
   ```

## Docker Deployment

For containerized deployment, use the provided Dockerfile:

1. Build the Docker image:
   ```bash
   docker build -t thinking-backend .
   ```

2. Run the container with the appropriate environment:
   ```bash
   # For development
   docker run -p 8000:8000 -e THINKING_ENV=dev thinking-backend
   
   # For production
   docker run -p 8000:8000 -e THINKING_ENV=prd thinking-backend
   ```

3. For production deployments, consider using Docker Compose or Kubernetes.

## Server Configuration

The server configuration is stored in each environment's config file under the `server` section:

```json
"server": {
  "host": "0.0.0.0",
  "port": 8000,
  "debug": false,
  "log_level": "warning"
}
```

Adjust these settings as needed for each environment.

## Deployment with Gunicorn

For production deployments, use Gunicorn as the WSGI server:

1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```

2. Start the application with Gunicorn:
   ```bash
   THINKING_ENV=prd gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

## Nginx Configuration

For production deployments, use Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name thinking.bot;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Health Checks

The backend provides a health check endpoint at `/api/health` that can be used by load balancers and monitoring systems.

## Monitoring

Consider setting up monitoring for the production environment:
- Use Prometheus for metrics collection
- Set up Grafana dashboards for visualization
- Configure alerts for service disruptions

## Backup and Recovery

Regularly back up your configuration files, especially those containing API keys.

## Security Considerations

- Never commit API keys to version control
- Use environment variables or a secure vault service for production API keys
- Restrict access to configuration management endpoints in production
- Set up proper firewall rules to restrict access to the backend
- Use HTTPS for all communications in production

# Frontend Deployment Guide

This guide explains how to deploy the Thinking Website frontend to different environments.

## Prerequisites

- Node.js 16+ installed
- npm or yarn package manager
- Git access to the repository
- Backend API deployed and accessible

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/thinking.git
   cd thinking/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn
   ```

3. Install required packages for markdown rendering and animations:
   ```bash
   npm install react-markdown remark-gfm
   # or
   yarn add react-markdown remark-gfm
   ```

4. Install TypeScript type definitions for Node.js (required for Tailwind animations):
   ```bash
   npm install --save-dev @types/node
   # or
   yarn add --dev @types/node
   ```

5. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

6. Configure environment variables:
   Create a `.env` file with the following variables:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   VITE_DEFAULT_LANGUAGE=en
   ```

   The `VITE_DEFAULT_LANGUAGE` environment variable controls the default language for the application. Currently supported values are:
   - `en` (English)
   - `zh` (Chinese)
   
   Note: Vite uses the `VITE_` prefix for environment variables instead of `REACT_APP_`.

7. The application will be available at `http://localhost:3000`

## Building for Production

1. Create environment-specific `.env` files:
   - `.env.development` - Development settings
   - `.env.test` - Testing environment settings
   - `.env.production` - Production settings

   Example `.env.production`:
   ```
   VITE_API_BASE_URL=https://api.thinking-app.com
   VITE_DEFAULT_LANGUAGE=en
   BUILD_SOURCEMAP=false
   ```

2. Build the application for the target environment:
   ```bash
   # For development
   npm run build -- --mode development
   # or
   yarn build --mode development

   # For testing
   npm run build -- --mode test
   # or
   yarn build --mode test

   # For production
   npm run build
   # or
   yarn build
   ```

3. The build output will be in the `build/` directory

## Deployment Options

### Static Site Hosting

The React application can be deployed to any static site hosting service:

#### Netlify

1. Connect your GitHub repository to Netlify
2. Configure build settings:
   - Build command: `npm run build` or `yarn build`
   - Publish directory: `build`
3. Configure environment variables in the Netlify dashboard
4. Deploy the site

#### Vercel

1. Connect your GitHub repository to Vercel
2. Configure build settings:
   - Framework preset: React
   - Build command: `npm run build` or `yarn build`
   - Output directory: `build`
3. Configure environment variables in the Vercel dashboard
4. Deploy the site

### Traditional Web Server (Nginx)

1. Build the application for production:
   ```bash
   npm run build
   # or
   yarn build
   ```

2. Copy the contents of the `build/` directory to your web server

3. Configure Nginx:
   ```nginx
   server {
       listen 80;
       server_name thinking-app.example.com;
       root /path/to/build;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       # Proxy API requests to the backend
       location /api {
           proxy_pass http://backend-server:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Deployment

1. Create a Dockerfile in the frontend directory:
   ```dockerfile
   FROM node:16-alpine as build
   WORKDIR /app
   COPY package*.json ./
   RUN npm install
   RUN npm install react-markdown remark-gfm @types/node --save
   COPY . .
   ARG VITE_API_BASE_URL
   ARG VITE_DEFAULT_LANGUAGE=en
   ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
   ENV VITE_DEFAULT_LANGUAGE=${VITE_DEFAULT_LANGUAGE}
   RUN npm run build

   FROM nginx:alpine
   COPY --from=build /app/build /usr/share/nginx/html
   COPY nginx.conf /etc/nginx/conf.d/default.conf
   EXPOSE 80
   CMD ["nginx", "-g", "daemon off;"]
   ```

2. Create an nginx.conf file:
   ```nginx
   server {
       listen 80;
       root /usr/share/nginx/html;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }
   }
   ```

3. Build and run the Docker container:
   ```bash
   docker build \
     --build-arg VITE_API_BASE_URL=https://api.thinking-app.com \
     --build-arg VITE_DEFAULT_LANGUAGE=en \
     -t thinking-frontend .
   docker run -p 80:80 thinking-frontend
   ```

## Continuous Integration/Continuous Deployment (CI/CD)

### GitHub Actions

Create a workflow file at `.github/workflows/deploy.yml`:

```yaml
name: Deploy Frontend

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
        
    - name: Install dependencies
      run: npm ci
      working-directory: ./frontend
      
    - name: Build
      run: npm run build
      working-directory: ./frontend
      env:
        VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
        
    - name: Deploy to Netlify
      uses: netlify/actions/cli@master
      with:
        args: deploy --dir=frontend/build --prod
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

## Environment-Specific Configurations

### Development Environment

- API Base URL: `VITE_API_BASE_URL=http://localhost:8000`
- Features: All features enabled, including debug tools
- Logging: Verbose

### Testing Environment

- API Base URL: `VITE_API_BASE_URL=https://test-api.thinking-app.com`
- Features: All production features, with some testing tools
- Logging: Standard

### Production Environment

- API Base URL: `VITE_API_BASE_URL=https://api.thinking-app.com`
- Features: Production features only
- Logging: Errors only
- Performance optimizations enabled

## Performance Optimization

1. Enable code splitting for production builds
2. Implement lazy loading for components
3. Use a CDN for static assets
4. Enable Gzip compression on the web server
5. Implement caching strategies
6. Use React.memo for frequently re-rendered components
7. Optimize animation performance with hardware acceleration

### Markdown Rendering Optimization

The application uses `react-markdown` with `remark-gfm` for rendering AI responses. To optimize performance:

1. Consider using the `rehype-sanitize` plugin for security in production
2. Implement lazy loading for the markdown renderer
3. Use the `skipHtml` option in sensitive environments to prevent XSS attacks

### Animation Performance

The application uses custom CSS animations for loading states. For optimal performance:

1. Use `will-change` CSS property sparingly for critical animations
2. Prefer CSS animations over JavaScript animations for UI effects
3. Use `transform` and `opacity` for animations when possible
4. Consider reducing animation complexity on low-power devices

## Monitoring and Analytics

1. Set up Google Analytics or a similar service
2. Implement error tracking with Sentry
3. Monitor performance with Lighthouse or WebPageTest

## Security Considerations

1. Always use HTTPS in production
2. Implement Content Security Policy (CSP)
3. Set secure and HttpOnly flags on cookies
4. Sanitize user inputs
5. Keep dependencies updated

## Localization

The application supports multiple languages with both frontend UI localization and backend response localization.

### Frontend Localization

The frontend uses the `VITE_DEFAULT_LANGUAGE` environment variable to determine the default language. Currently supported values:
- `en` (English)
- `zh` (Chinese)

### Backend Localization

The backend API accepts a `language` parameter in requests to the `/api/chat` and `/api/summary` endpoints. This allows for generating AI responses and summaries in the user's preferred language.

### Deployment Considerations for Localization

1. Ensure all UI strings are properly translated before deploying
2. Test the application with different language settings
3. Verify that AI responses are correctly generated in all supported languages
4. Consider region-specific deployments for better performance in different geographic areas

## Accessibility

Verify that the application meets accessibility standards (WCAG 2.1) before deploying to production.

## Browser Compatibility

Test the application in all major browsers before deploying to production:
- Chrome
- Firefox
- Safari
- Edge
