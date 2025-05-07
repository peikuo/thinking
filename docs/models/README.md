# AI Models in the Thinking Platform

This guide provides information about the AI models supported by the Thinking platform, their configuration, and specific features.

## Supported Models

The Thinking platform currently supports the following AI models:

| Model | Provider | Primary Language | Environment Variables |
|-------|----------|------------------|----------------------|
| GPT-4.1-mini | OpenAI | English | `OPENAI_API_KEY`, `OPENAI_API_URL`, `OPENAI_MODEL` |
| Grok-2-latest | X.AI (formerly Twitter) | English | `GROK_API_KEY`, `GROK_API_URL`, `GROK_MODEL` |
| Qwen-plus | Alibaba Cloud | English/Chinese | `QWEN_API_KEY`, `QWEN_API_URL`, `QWEN_MODEL` |
| DeepSeek-chat | DeepSeek | English/Chinese | `DEEPSEEK_API_KEY`, `DEEPSEEK_API_URL`, `DEEPSEEK_MODEL` |
| GLM-4-Air-250414 | Zhipu AI | Chinese | `GLM_API_KEY`, `GLM_API_URL`, `GLM_MODEL` |
| Doubao-1-5-pro-32k-250115 | Doubao | Chinese | `DOUBAO_API_KEY`, `DOUBAO_API_URL`, `DOUBAO_MODEL` |

## Language-Based Model Selection

The Thinking platform automatically selects appropriate models based on the detected language of the user query:

### English Language Queries
- OpenAI (GPT-4.1-mini)
- Grok (grok-2-latest)
- Qwen (qwen-plus)
- DeepSeek (deepseek-chat)

### Chinese Language Queries
- DeepSeek (deepseek-chat)
- Qwen (qwen-plus)
- Doubao (doubao-1-5-pro-32k-250115)
- GLM (GLM-4-Air-250414)

## Model Configuration

### Environment Variables

Each model requires specific environment variables to be set in the `.env` file:

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

### Obtaining API Keys

- **OpenAI**: Sign up at [OpenAI Platform](https://platform.openai.com/)
- **Grok**: Available through [X.AI](https://x.ai/)
- **Qwen**: Available through [Alibaba Cloud](https://www.alibabacloud.com/)
- **DeepSeek**: Sign up at [DeepSeek](https://www.deepseek.com/)
- **GLM**: Available through [Zhipu AI](https://open.bigmodel.cn/)
- **Doubao**: Available through [Doubao](https://www.doubao.com/)

## Model-Specific Features

### HTML Rendering

The platform supports HTML rendering in table cells using rehype-raw, which is particularly important for models that return formatted HTML content.

### Summary Generation

The summary generation feature uses language-appropriate models:
- For English summaries: OpenAI or Grok models are preferred
- For Chinese summaries: DeepSeek, Qwen, Doubao, or GLM models are preferred

## Adding New Models

To add a new model to the Thinking platform:

1. Add the model's environment variables to `.env.example` and your local `.env` file
2. Create a new API endpoint in the backend
3. Add the model to the language-based selection logic
4. Update the frontend to include the new model in the UI

For detailed implementation instructions, refer to the [Development Guide](../development/README.md).
