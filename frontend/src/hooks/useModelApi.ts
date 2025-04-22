import { useState, useCallback, useEffect } from 'react';
import { queryAllModels, requestSummary } from '@/lib/api';
import { ModelResponse, ComparisonSummary, ConversationMessage } from '@/types/models';
import { ApiKeys } from './useApiKeys';
import { useLanguage } from '@/contexts/LanguageContext';

// Interface for streaming updates
interface StreamingState {
  openai: string;
  grok: string;
  qwen: string;
  deepseek: string;
  doubao: string;
  glm: string;
  summary: string;
}

// Storage key for saving partial responses
const STREAMING_STORAGE_KEY = 'thinking-streaming-content';

export function useModelApi() {
  const [loading, setLoading] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streamingContent, setStreamingContent] = useState<StreamingState>(() => {
    // Try to restore streaming content from localStorage on initial load
    try {
      const saved = localStorage.getItem(STREAMING_STORAGE_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.error('Failed to parse saved streaming content', e);
    }
    
    // Default empty state
    return {
      openai: '',
      grok: '',
      qwen: '',
      deepseek: '',
      doubao: '',
      glm: '',
      summary: ''
    };
  });
  const [isStreaming, setIsStreaming] = useState(false);
  const { language } = useLanguage();
  
  // Save streaming content to localStorage whenever it changes
  useEffect(() => {
    if (Object.values(streamingContent).some(content => content.length > 0)) {
      localStorage.setItem(STREAMING_STORAGE_KEY, JSON.stringify(streamingContent));
    }
  }, [streamingContent]);

  const queryModels = useCallback(async (
    prompt: string,
    apiKeys: ApiKeys,
    useStreaming: boolean = true,
    selectedModels?: string[],
    conversationHistory?: ConversationMessage[]
  ): Promise<{
    modelResponses: ModelResponse[],
    summary: ComparisonSummary
  } | null> => {
    // Declare updateInterval at function scope to fix TypeScript errors
    let updateInterval: NodeJS.Timeout | null = null;
    setLoading(true);
    setError(null);
    
    // Reset streaming content if using streaming mode
    if (useStreaming) {
      // Clear previous streaming content
      const emptyContent = {
        openai: '',
        grok: '',
        qwen: '',
        deepseek: '',
        doubao: '',
        glm: '',
        summary: ''
      };
      setStreamingContent(emptyContent);
      setIsStreaming(false);
      
      // Clear from localStorage to avoid restoring old content on refresh
      localStorage.removeItem(STREAMING_STORAGE_KEY);
    }
    
    try {
      // Define streaming update handler
          // Use a buffer-based approach with much less frequent updates
      // This will drastically reduce re-renders
      const buffers: Record<string, string[]> = {
        openai: [],
        grok: [],
        qwen: [],
        deepseek: [],
        doubao: [],
        glm: [],
        summary: []
      };
      
      // updateInterval is now declared at function scope
      
      const handleStreamUpdate = useStreaming ? 
        (model: string, content: string) => {
          // Just add content to buffer, don't update state yet
          buffers[model].push(content);
          
          // Set streaming flag once at the beginning
          if (!isStreaming && !updateInterval) {
            setIsStreaming(true);
            
            // Set up an interval that updates the UI much less frequently
            // This is the key to preventing flickering - update at most every 300ms
            updateInterval = setInterval(() => {
              // Only update if there's content in the buffers
              const hasContent = Object.values(buffers).some(buffer => buffer.length > 0);
              
              if (hasContent) {
                setStreamingContent(prev => {
                  const newContent = { ...prev };
                  
                  // Process all buffered content for each model
                  Object.keys(buffers).forEach(modelKey => {
                    if (buffers[modelKey].length > 0) {
                      // Join all buffered content and add to existing content
                      newContent[modelKey as keyof StreamingState] += buffers[modelKey].join('');
                      // Clear the buffer
                      buffers[modelKey] = [];
                    }
                  });
                  
                  return newContent;
                });
              }
            }, 300); // Update UI at most every 300ms
          }
        } : undefined;
      
      // Get model responses with streaming updates if enabled
      const result = await queryAllModels(prompt, apiKeys, language, handleStreamUpdate, selectedModels, conversationHistory);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Error querying models:', errorMessage);
      return null;
    } finally {
      setLoading(false);
      if (useStreaming) {
        setIsStreaming(false);
        // Clear the update interval
        if (updateInterval) {
          clearInterval(updateInterval);
          updateInterval = null;
        }
      }
    }
  }, [language]);
  
  const generateSummary = useCallback(async (
    prompt: string,
    modelResponses: ModelResponse[],
    apiKeys: ApiKeys,
    useStreaming: boolean = true
  ): Promise<ComparisonSummary> => {
    // Filter model responses based on language
    // For Chinese, include GLM and Doubao; for English, include OpenAI and Grok
    const relevantModels = language === 'zh'
      ? ['deepseek', 'qwen', 'doubao', 'glm']
      : ['openai', 'grok', 'qwen', 'deepseek'];
    
    // Only include responses from models relevant to the current language
    const filteredResponses = modelResponses.filter(response => 
      relevantModels.includes(response.model as string)
    );
    setSummaryLoading(true);
    
    // Reset summary streaming content
    if (useStreaming) {
      setStreamingContent(prev => ({
        ...prev,
        summary: ''
      }));
      setIsStreaming(false);
    }
    
    // Declare buffers for summary streaming
    const summaryBuffer: string[] = [];
    let summaryUpdateInterval: NodeJS.Timeout | null = null;
    
    try {
      // Define streaming update handler for summary
      const handleSummaryUpdate = useStreaming ? 
        (content: string) => {
          console.log('Summary streaming update received:', content);
          
          // Set streaming flag once at the beginning
          if (!isStreaming && !summaryUpdateInterval) {
            console.log('Setting isStreaming to true for summary');
            setIsStreaming(true);
            
            // Set up an interval that updates the UI less frequently
            summaryUpdateInterval = setInterval(() => {
              if (summaryBuffer.length > 0) {
                console.log('Updating summary content with buffer:', summaryBuffer.join(''));
                setStreamingContent(prev => {
                  const newContent = { ...prev };
                  newContent.summary += summaryBuffer.join('');
                  // Clear the buffer
                  summaryBuffer.length = 0;
                  return newContent;
                });
              }
            }, 300); // Update UI every 300ms
          }
          
          // Add to buffer instead of updating state directly
          summaryBuffer.push(content);
        } : undefined;
      
      // Request summary separately after model responses are rendered
      const summary = await requestSummary(prompt, filteredResponses, apiKeys, language, handleSummaryUpdate);
      return summary;
    } catch (err) {
      console.error('Error generating summary:', err);
      return { content: "" };
    } finally {
      setSummaryLoading(false);
      if (summaryUpdateInterval) {
        clearInterval(summaryUpdateInterval);
        summaryUpdateInterval = null;
      }
      if (useStreaming) {
        // Make sure any remaining buffered content is displayed
        if (summaryBuffer && summaryBuffer.length > 0) {
          setStreamingContent(prev => ({
            ...prev,
            summary: prev.summary + summaryBuffer.join('')
          }));
        }
        // Reset streaming state after a short delay
        setTimeout(() => {
          setIsStreaming(false);
        }, 500);
      }
    }
  }, [language]);
  
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    summaryLoading,
    error,
    streamingContent,
    isStreaming,
    queryModels,
    generateSummary,
    clearError
  };
}
