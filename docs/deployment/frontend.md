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
   yarn install
   ```

3. Configure environment variables:
   Create a `.env.local` file with the following variables:
   ```
   REACT_APP_API_BASE_URL=http://localhost:8000
   REACT_APP_DEFAULT_LANGUAGE=en
   ```

4. Start the development server:
   ```bash
   npm start
   # or
   yarn start
   ```

5. The application will be available at `http://localhost:3000`

## Building for Production

1. Create environment-specific `.env` files:
   - `.env.development` - Development settings
   - `.env.test` - Testing environment settings
   - `.env.production` - Production settings

   Example `.env.production`:
   ```
   REACT_APP_API_BASE_URL=https://api.thinking-app.com
   REACT_APP_DEFAULT_LANGUAGE=en
   GENERATE_SOURCEMAP=false
   ```

2. Build the application for the target environment:
   ```bash
   # For development
   npm run build:dev
   # or
   yarn build:dev

   # For testing
   npm run build:test
   # or
   yarn build:test

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
   COPY . .
   ARG REACT_APP_API_BASE_URL
   ENV REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL}
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
   docker build --build-arg REACT_APP_API_BASE_URL=https://api.thinking-app.com -t thinking-frontend .
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
        REACT_APP_API_BASE_URL: ${{ secrets.REACT_APP_API_BASE_URL }}
        
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

- API Base URL: `http://localhost:8000`
- Features: All features enabled, including debug tools
- Logging: Verbose

### Testing Environment

- API Base URL: `https://test-api.thinking-app.com`
- Features: All production features, with some testing tools
- Logging: Standard

### Production Environment

- API Base URL: `https://api.thinking-app.com`
- Features: Production features only
- Logging: Errors only
- Performance optimizations enabled

## Performance Optimization

1. Enable code splitting for production builds
2. Implement lazy loading for components
3. Use a CDN for static assets
4. Enable Gzip compression on the web server
5. Implement caching strategies

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

The application supports multiple languages. Ensure all translations are complete before deploying to production.

## Accessibility

Verify that the application meets accessibility standards (WCAG 2.1) before deploying to production.

## Browser Compatibility

Test the application in all major browsers before deploying to production:
- Chrome
- Firefox
- Safari
- Edge
