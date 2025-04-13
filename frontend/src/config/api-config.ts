
export interface ApiConfig {
  endpoints: {
    openai: string;
    grok: string;
    qwen: string;
    deepseek: string;
  };
  timeouts: {
    default: number;
  };
}

const apiConfig: ApiConfig = {
  endpoints: {
    openai: "https://api.openai.com/v1/chat/completions",
    grok: "https://api.grok.ai/v1/chat/completions", // Placeholder
    qwen: "https://api.qwen.ai/v1/chat/completions", // Placeholder
    deepseek: "https://api.deepseek.ai/v1/chat/completions" // Placeholder
  },
  timeouts: {
    default: 30000 // 30 seconds
  }
};

export default apiConfig;
