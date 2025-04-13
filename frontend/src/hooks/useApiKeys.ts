import { useState, useEffect, useCallback } from 'react';

export interface ApiKeys extends Record<string, string> {
  openai: string;
  grok: string;
  qwen: string;
  deepseek: string;
}

export function useApiKeys() {
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    openai: "",
    grok: "",
    qwen: "",
    deepseek: ""
  });

  // Load API keys from localStorage on mount
  useEffect(() => {
    const savedApiKeys = localStorage.getItem('ai-comparison-api-keys');
    if (savedApiKeys) {
      try {
        setApiKeys(JSON.parse(savedApiKeys));
      } catch (e) {
        console.error('Failed to parse API keys', e);
      }
    }
  }, []);

  // Save API keys to localStorage when they change
  const saveApiKeys = useCallback((keys: ApiKeys) => {
    setApiKeys(keys);
    localStorage.setItem('ai-comparison-api-keys', JSON.stringify(keys));
  }, []);

  return {
    apiKeys,
    saveApiKeys
  };
}
