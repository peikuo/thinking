import { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { requestSequentialDiscussion } from '@/lib/discuss-api';
import { ApiKeys } from './useApiKeys';
import { toast } from 'sonner';

export type DiscussResponse = {
  model: string;
  content: string;
  loading?: boolean;
};

export function useDiscussMode() {
  const [responses, setResponses] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [streamingModel, setStreamingModel] = useState<string | null>(null);
  const { language } = useLanguage();

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
          setResponses(prev => ({ ...prev, [model]: content }));
          
          // Only increment step when moving to a new model
          setResponses(prev => {
            // Only increment step when this is a new model (not already in responses)
            if (!prev[model]) {
              setCurrentStep(currentStep => currentStep + 1);
            }
            return { ...prev, [model]: content };
          });
        }
      );
      
      // Final update with all responses
      setResponses(results);
    } catch (error) {
      console.error('Error in discussion mode:', error);
      toast.error('Failed to complete the discussion');
    } finally {
      setLoading(false);
    }
  };

  return {
    responses,
    loading,
    currentStep,
    streamingModel,
    startDiscussion,
    getModelOrder
  };
}
