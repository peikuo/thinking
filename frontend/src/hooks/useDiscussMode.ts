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
    
    const modelOrder = getModelOrder();
    
    try {
      const results = await requestSequentialDiscussion(
        prompt,
        modelOrder as any, // TypeScript fix
        apiKeys,
        language,
        (model, content) => {
          // Update responses as they come in
          setResponses(prev => ({ ...prev, [model]: content }));
          setCurrentStep(prev => prev + 1);
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
    totalSteps: getModelOrder().length,
    startDiscussion
  };
}
