
export interface ModelResponse {
  model: 'openai' | 'grok' | 'qwen' | 'deepseek' | 'doubao' | 'glm' | 'summary';
  content: string;
  loading?: boolean;
  error?: string;
}

export interface ComparisonSummary {
  // Single markdown content field for the entire summary
  content: string;
  // Flag to indicate if summary should be skipped (when only one model is selected)
  skipSummary?: boolean;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  modelResponses?: ModelResponse[];
  summary?: ComparisonSummary;
  selectedModels?: string[];
}

export interface StreamingState {
  openai: string;
  grok: string;
  qwen: string;
  deepseek: string;
  doubao: string;
  glm: string;
  summary: string;
}
