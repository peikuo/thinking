# Thinking Platform Deployment Guide

This directory contains comprehensive deployment guides for the Thinking AI Model Comparison Platform across different environments and configurations.

## Available Deployment Guides

- [Aliyun Cloud Deployment](aliyun.md) - Deploy on Aliyun Cloud ECS instances
- [Aliyun Cloud Deployment (Chinese)](aliyun_cn.md) - Aliyun Cloud deployment guide in Chinese
- [Docker Deployment](docker.md) - Deploy using Docker containers
- [Frontend Deployment](frontend.md) - Specific instructions for deploying the frontend
- [Proxy Deployment](proxy.md) - Guide for deploying the proxy component

## Quick Start

For most users, we recommend starting with either:

1. [Aliyun Cloud Deployment](aliyun.md) for production deployments in China
2. [Docker Deployment](docker.md) for quick setup and testing

## Common Deployment Tasks

### Environment Variables

All components of the Thinking platform require specific environment variables for proper operation. Make sure to set up the following environment variables for each model:

```
# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_URL=https://api.openai.com/v1/chat/completions
OPENAI_MODEL=gpt-4.1-mini

# Grok
GROK_API_KEY=your_grok_api_key
GROK_API_URL=https://api.x.ai/v1
GROK_MODEL=grok-2-latest

# Qwen
QWEN_API_KEY=your_qwen_api_key
QWEN_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# GLM
GLM_API_KEY=your_glm_api_key
GLM_API_URL=https://open.bigmodel.cn/api/paas/v4
GLM_MODEL=GLM-4-Air-250414

# Doubao
DOUBAO_API_KEY=your_doubao_api_key
DOUBAO_API_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-1-5-pro-32k-250115
```

### Troubleshooting

If you encounter issues during deployment, please refer to the [Troubleshooting Guide](../troubleshooting/README.md) for common problems and solutions.
