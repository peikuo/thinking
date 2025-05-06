import { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { requestSequentialDiscussion } from '@/lib/discuss-api';
import { ApiKeys } from './useApiKeys';
import { toast } from 'sonner';

export type DiscussResponse = {
  model: string;
  content: string;
  loading?: boolean;
};

// Storage keys for saving discuss mode responses
const DISCUSS_STORAGE_KEY = 'thinking-discuss-responses';
const DISCUSS_PROMPT_KEY = 'thinking-discuss-prompt';
const CONVERSATION_STORAGE_KEY = 'ai-comparison-conversations';

export function useDiscussMode() {
  const [responses, setResponses] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [streamingModel, setStreamingModel] = useState<string | null>(null);
  const [lastPrompt, setLastPrompt] = useState<string>('');
  const { language } = useLanguage();
  
  // Load responses from localStorage on mount
  useEffect(() => {
    try {
      const savedResponses = localStorage.getItem(DISCUSS_STORAGE_KEY);
      const savedPrompt = localStorage.getItem(DISCUSS_PROMPT_KEY);
      
      if (savedResponses) {
        setResponses(JSON.parse(savedResponses));
      }
      
      if (savedPrompt) {
        setLastPrompt(savedPrompt);
      }
    } catch (error) {
      console.error('Error loading discuss responses from localStorage:', error);
    }
  }, []);
  
  // Save responses to localStorage when they change
  useEffect(() => {
    if (Object.keys(responses).length > 0) {
      localStorage.setItem(DISCUSS_STORAGE_KEY, JSON.stringify(responses));
    }
  }, [responses]);

  // Define the model order based on the language
  const getModelOrder = () => {
    return language === 'zh' 
      ? ['glm', 'doubao', 'deepseek', 'qwen'] 
      : ['openai', 'grok', 'qwen', 'deepseek'];
  };

  const startDiscussion = async (
    prompt: string,
    apiKeys: ApiKeys
  ) => {
    setLoading(true);
    setResponses({});
    setCurrentStep(0);
    setStreamingModel(null);
    setLastPrompt(prompt);
    
    // Save prompt to localStorage
    localStorage.setItem(DISCUSS_PROMPT_KEY, prompt);
    
    // Save to conversation history
    try {
      const savedConversations = localStorage.getItem(CONVERSATION_STORAGE_KEY);
      if (savedConversations) {
        const conversations = JSON.parse(savedConversations);
        const timestamp = Date.now();
        
        // Create a new conversation for this discussion
        // Use the prompt directly as the title (simple approach)
        const title = prompt.length > 30 ? prompt.substring(0, 30) + '...' : prompt;
        
        const newDiscussion = {
          id: `discuss-${timestamp}`,
          title: title, // Use the prompt as the title immediately
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ],
          timestamp: timestamp,
          isDiscussMode: true // Mark this as a discuss mode conversation
        };
        
        // Add to conversations and save
        const updatedConversations = [newDiscussion, ...conversations];
        localStorage.setItem(CONVERSATION_STORAGE_KEY, JSON.stringify(updatedConversations));
      }
    } catch (error) {
      console.error('Error saving to conversation history:', error);
    }
    
    const modelOrder = getModelOrder();
    
    try {
      const results = await requestSequentialDiscussion(
        prompt,
        modelOrder as any, // TypeScript fix
        apiKeys,
        language,
        (model, content) => {
          // Update responses as they come in
          setStreamingModel(model);
          
          // Update responses and increment step in a more reliable way
          setResponses(prev => {
            const updatedResponses = { ...prev, [model]: content };
            
            // Calculate the current step based on the number of models that have responded
            // This is more reliable than incrementing
            const modelIndex = modelOrder.indexOf(model);
            if (modelIndex !== -1 && (!prev[model] || Object.keys(prev).length === 0)) {
              // If this is a new model response, update the step
              // Add 1 because steps are 1-indexed in the UI
              setCurrentStep(modelIndex + 1);
            }
            
            return updatedResponses;
          });
          
          // Update conversation history with the latest responses
          try {
            const savedConversations = localStorage.getItem(CONVERSATION_STORAGE_KEY);
            if (savedConversations) {
              const conversations = JSON.parse(savedConversations);
              if (conversations.length > 0 && conversations[0].isDiscussMode) {
                // Get current responses state
                const currentResponses = { ...responses };
                // Update with the latest response
                currentResponses[model] = content;
                
                const assistantMessage = {
                  role: 'assistant',
                  content: Object.values(currentResponses).join('\n\n---\n\n'),
                  modelResponses: Object.entries(currentResponses).map(([modelName, modelContent]) => ({
                    model: modelName,
                    content: modelContent,
                    loading: false
                  }))
                };
                
                // Update the messages
                if (conversations[0].messages.length > 1) {
                  // Replace the existing assistant message
                  conversations[0].messages[1] = assistantMessage;
                } else {
                  // Add a new assistant message
                  conversations[0].messages.push(assistantMessage);
                }
                
                localStorage.setItem(CONVERSATION_STORAGE_KEY, JSON.stringify(conversations));
              }
            }
          } catch (error) {
            console.error('Error updating conversation history:', error);
          }
        }
      );
      
      // Final update with all responses
      setResponses(results);
      // Reset streaming model when all models are done
      setStreamingModel(null);
      
      // Final update to conversation history
      try {
        const savedConversations = localStorage.getItem(CONVERSATION_STORAGE_KEY);
        if (savedConversations) {
          const conversations = JSON.parse(savedConversations);
          if (conversations.length > 0 && conversations[0].isDiscussMode) {
            // Update the first conversation with the final results
            const assistantMessage = {
              role: 'assistant',
              content: Object.values(results).join('\n\n---\n\n'),
              modelResponses: Object.entries(results).map(([model, content]) => ({
                model,
                content,
                loading: false
              }))
            };
            
            // Update the messages
            if (conversations[0].messages.length > 1) {
              // Replace the existing assistant message
              conversations[0].messages[1] = assistantMessage;
            } else {
              // Add a new assistant message
              conversations[0].messages.push(assistantMessage);
            }
            
            localStorage.setItem(CONVERSATION_STORAGE_KEY, JSON.stringify(conversations));
          }
        }
      } catch (error) {
        console.error('Error finalizing conversation history:', error);
      }
    } catch (error) {
      console.error('Error in discussion mode:', error);
      toast.error('Failed to complete the discussion');
    } finally {
      setLoading(false);
    }
  };

  // Reset all discuss mode state
  const resetDiscussion = useCallback(() => {
    setResponses({});
    setCurrentStep(0);
    setStreamingModel(null);
    setLastPrompt('');
    
    // Clear discuss mode localStorage
    localStorage.removeItem(DISCUSS_STORAGE_KEY);
    localStorage.removeItem(DISCUSS_PROMPT_KEY);
    
    // Update conversation history to preserve it between modes
    try {
      const savedConversations = localStorage.getItem(CONVERSATION_STORAGE_KEY);
      if (savedConversations) {
        const conversations = JSON.parse(savedConversations);
        
        // Check if we need to add a new discussion conversation
        // We don't need to add one here since we're now creating it in useNewConversation
        // before calling resetDiscussion
        
        // Keep the conversations but clear any active discuss mode data
        localStorage.setItem(CONVERSATION_STORAGE_KEY, JSON.stringify(conversations));
      }
    } catch (error) {
      console.error('Error updating conversation history:', error);
    }
  }, []);

  return {
    responses,
    loading,
    currentStep,
    streamingModel,
    lastPrompt,
    startDiscussion,
    getModelOrder,
    resetDiscussion
  };
}
