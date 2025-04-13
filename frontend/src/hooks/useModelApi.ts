import { useState, useCallback } from 'react';
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
  summary: string;
}

export function useModelApi() {
  const [loading, setLoading] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streamingContent, setStreamingContent] = useState<StreamingState>({
    openai: '',
    grok: '',
    qwen: '',
    deepseek: '',
    summary: ''
  });
  const [isStreaming, setIsStreaming] = useState(false);
  const { language } = useLanguage();

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
      setStreamingContent({
        openai: '',
        grok: '',
        qwen: '',
        deepseek: '',
        summary: ''
      });
      setIsStreaming(false);
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
      const summary = await requestSummary(prompt, modelResponses, apiKeys, language, handleSummaryUpdate);
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
