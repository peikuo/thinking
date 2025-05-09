// Utility to get locale-aware display name for models
export function getModelDisplayName(model: string, language: string) {
  if (language === 'zh') {
    switch (model) {
      case 'qwen': return '通义千问';
      case 'deepseek': return '深度求索';
      case 'glm': return '智谱';
      case 'doubao': return '豆包';
      case 'openai': return 'OpenAI';
      case 'grok': return 'Grok';
      case 'summary': return '总结';
      default: return model;
    }
  } else {
    switch (model) {
      case 'qwen': return 'Qwen';
      case 'deepseek': return 'DeepSeek';
      case 'glm': return 'GLM';
      case 'doubao': return 'Doubao';
      case 'openai': return 'OpenAI';
      case 'grok': return 'Grok';
      case 'summary': return 'Summary';
      default: return model;
    }
  }
}
