
import React, { createContext, useContext, useState, useEffect } from 'react';

type Language = 'en' | 'zh';

type Translations = {
  [key: string]: {
    en: string;
    zh: string;
  };
};

// All translatable strings in the application
const translations: Translations = {
  newConversation: {
    en: "New",
    zh: "新对话"
  },
  welcome: {
    en: "Welcome to Thinking Together",
    zh: "欢迎使用集思广益"
  },
  welcomeDescription: {
    en: "Ask a question to see how different AI models respond. We'll show you responses from OpenAI, Grok, Qwen, and DeepSeek, along with a summary of their similarities and differences.",
    zh: "提出问题，查看不同 AI 模型的回应。我们将展示 OpenAI、Grok、Qwen 和 DeepSeek 的回应，并总结它们的异同点。"
  },
  history: {
    en: "History",
    zh: "历史记录"
  },
  noHistoryYet: {
    en: "No conversation history yet",
    zh: "暂无对话历史"
  },
  conversationsWillAppear: {
    en: "Your conversations will appear here",
    zh: "您的对话将显示在这里"
  },
  storedLocally: {
    en: "Conversations are stored locally in your browser",
    zh: "对话存储在您的浏览器本地"
  },
  today: {
    en: "Today",
    zh: "今天"
  },
  yesterday: {
    en: "Yesterday",
    zh: "昨天"
  },
  older: {
    en: "Older",
    zh: "更早"
  },
  last30Days: {
    en: "Last 30 Days",
    zh: "前 30 天"
  },
  threeDaysAgo: {
    en: "3 days ago",
    zh: "三天前"
  },
  sevenDaysAgo: {
    en: "7 days ago",
    zh: "七天前"
  },
  halfYearAgo: {
    en: "Half year ago",
    zh: "半年前"
  },
  oneYearAgo: {
    en: "One year ago",
    zh: "一年前"
  },
  generateSummary: {
    en: "Generate Summary",
    zh: "生成总结"
  },
  generatingSummary: {
    en: "Generating Summary...",
    zh: "正在生成总结..."
  },
  summary: {
    en: "Summary",
    zh: "总结"
  },
  summaryError: {
    en: "Error generating summary. Please try again.",
    zh: "生成总结时出错。请重试。"
  },
  responsesGenerated: {
    en: "Responses generated",
    zh: "已生成回应"
  },
  allModelsResponded: {
    en: "All AI models have responded to your question",
    zh: "所有 AI 模型已回应您的问题"
  },
  selectedModelsResponded: {
    en: "Selected AI models have responded to your question",
    zh: "已选择的 AI 模型已回应您的问题"
  },
  responseGenerated: {
    en: "Response generated",
    zh: "已生成回应"
  },
  modelResponded: {
    en: "The {model} model has responded to your question",
    zh: "{model} 模型已回应您的问题"
  },
  selectModel: {
    en: "Select a model",
    zh: "选择模型"
  },
  error: {
    en: "Error",
    zh: "错误"
  },
  failedToGetResponses: {
    en: "Failed to get responses from AI models",
    zh: "无法获取 AI 模型的回应"
  },
  recentConversations: {
    en: "Recent Conversations",
    zh: "最近对话"
  },
  compare: {
    en: "Thinking Together",
    zh: "集思广益"
  },
  modelWillRespond: {
    en: "Combining the wisdom of multiple AI models",
    zh: "汇集多个AI模型的智慧"
  },
  hideHistory: {
    en: "Hide history sidebar",
    zh: "隐藏历史记录"
  },
  showHistory: {
    en: "Show history sidebar",
    zh: "显示历史记录"
  },
  apiKeys: {
    en: "API Keys",
    zh: "API 密钥"
  },
  apiKeysDescription: {
    en: "Enter your API keys for each model. Your keys are only stored in your browser.",
    zh: "输入每个模型的 API 密钥。您的密钥仅存储在您的浏览器中。"
  },
  save: {
    en: "Save",
    zh: "保存"
  },
  openaiKey: {
    en: "OpenAI API Key",
    zh: "OpenAI API 密钥"
  },
  grokKey: {
    en: "Grok API Key",
    zh: "Grok API 密钥"
  },
  qwenKey: {
    en: "Qwen API Key",
    zh: "Qwen API 密钥"
  },
  deepseekKey: {
    en: "DeepSeek API Key",
    zh: "DeepSeek API 密钥"
  },
  glmKey: {
    en: "GLM API Key",
    zh: "GLM API 密钥"
  },
  doubaoKey: {
    en: "Doubao API Key",
    zh: "Doubao API 密钥"
  },
  chatMode: {
    en: "Chat Mode",
    zh: "聊天模式"
  },
  discussMode: {
    en: "Discuss Mode",
    zh: "讨论模式"
  },
  discussDescription: {
    en: "Models analyze each other's responses sequentially",
    zh: "模型依次分析彼此的回答"
  },
  discussingModels: {
    en: "Discussing {current} of {total} models",
    zh: "正在讨论第 {current} 个模型（共 {total} 个）"
  },
  generating: {
    en: "Generating response...",
    zh: "正在生成回答..."
  },
  streaming: {
    en: "Streaming",
    zh: "实时生成中"
  },
  waitingForPreviousModel: {
    en: "Waiting for previous model's response",
    zh: "等待前一个模型的响应"
  },
  inputPlaceholder: {
    en: "Ask any question to compare AI model responses...",
    zh: "提出问题，汇集多个 AI 模型的智慧..."
  },
  send: {
    en: "Send",
    zh: "发送"
  },
  processing: {
    en: "Processing...",
    zh: "处理中..."
  },
  delete: {
    en: "Delete",
    zh: "删除"
  },
  cancel: {
    en: "Cancel",
    zh: "取消"
  },
  deleteConfirmationTitle: {
    en: "Are you sure?",
    zh: "确定要删除吗？"
  },
  deleteConfirmation: {
    en: "This action cannot be undone. This will permanently delete the conversation.",
    zh: "此操作无法撤销。这将永久删除该对话。"
  },
  deleteConfirmationWithTitle: {
    en: "This action cannot be undone. This will permanently delete the conversation '{title}'.",
    zh: "此操作无法撤销。这将永久删除对话“{title}”。"
  },
  aiResponseComparison: {
    en: "AI Response Comparison",
    zh: "AI 回答总结"
  },
  shortcutTip: {
    en: "Press Enter to send (Shift+Enter for new line)",
    zh: "按 Enter 发送 (Shift+Enter 换行)"
  },
  switchToCompactLayout: {
    en: "Switch to compact layout",
    zh: "切换到紧凑布局"
  },
  switchToDefaultLayout: {
    en: "Switch to default layout",
    zh: "切换到默认布局"
  },
  youAsked: {
    en: "You asked:",
    zh: "您提问的是:"
  },
  exportAsMarkdown: {
    en: "Export as Markdown",
    zh: "导出为 Markdown"
  },
  noContent: {
    en: "No Content",
    zh: "无内容"
  },
  noContentToExport: {
    en: "There is no conversation content to export",
    zh: "没有可导出的对话内容"
  },
  exportSuccess: {
    en: "Export Successful",
    zh: "导出成功"
  },
  conversationExported: {
    en: "Conversation has been exported as markdown",
    zh: "对话已导出为 markdown 格式"
  },
  clearAllHistory: {
    en: "Clear History",
    zh: "清空历史"
  },
  clearAllHistoryConfirm: {
    en: "Are you sure you want to clear all conversation history? This action cannot be undone.",
    zh: "确定要清空所有对话历史吗？此操作无法撤销。"
  },
  deleteConversation: {
    en: "Delete Conversation",
    zh: "删除对话"
  },
  deleteConversationConfirm: {
    en: "Are you sure you want to delete this conversation? This action cannot be undone.",
    zh: "确定要删除此对话吗？此操作无法撤销。"
  }
};

type LanguageContextType = {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, params?: Record<string, string>) => string;
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Get initial language from localStorage or browser language
  const getInitialLanguage = (): Language => {
    const savedLanguage = localStorage.getItem('ai-comparison-language');
    if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'zh')) {
      return savedLanguage;
    }
    // Use browser language as fallback
    return navigator.language.startsWith('zh') ? 'zh' : 'en';
  };

  const [language, setLanguage] = useState<Language>(getInitialLanguage());

  // Save language preference to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('ai-comparison-language', language);
  }, [language]);

  // Translation function with parameter support
  const t = (key: string, params?: Record<string, string>): string => {
    if (!translations[key]) {
      console.warn(`Translation missing for key: ${key}`);
      return key;
    }
    
    let translatedText = translations[key][language];
    
    // Replace parameters if provided
    if (params) {
      Object.entries(params).forEach(([param, value]) => {
        translatedText = translatedText.replace(`{${param}}`, value);
      });
    }
    
    return translatedText;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

// Custom hook to use the language context
export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
