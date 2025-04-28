import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { useLanguage } from '@/contexts/LanguageContext';
import Markdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';

interface DiscussionThreadProps {
  userPrompt: string;
  responses: Record<string, string>;
  loading: boolean;
  currentStep: number;
  streamingModel: string | null;
}

// Get model initials for avatar
const getModelInitials = (modelName: string): string => {
  return modelName.substring(0, 2).toUpperCase();
};

// Get model color class
const getModelColorClass = (modelName: string): string => {
  const colorMap: Record<string, string> = {
    openai: 'bg-model-openai',
    grok: 'bg-model-grok',
    qwen: 'bg-model-qwen',
    deepseek: 'bg-model-deepseek',
    glm: 'bg-green-500',
    doubao: 'bg-purple-500',
  };
  
  return colorMap[modelName] || 'bg-gray-500';
};

const DiscussionThread: React.FC<DiscussionThreadProps> = ({
  userPrompt,
  responses,
  loading,
  currentStep,
  streamingModel
}) => {
  const { t, language } = useLanguage();
  
  // Determine the model order based on language
  const modelOrder = language === 'zh' 
    ? ['glm', 'doubao', 'deepseek', 'qwen'] 
    : ['openai', 'grok', 'qwen', 'deepseek'];
    
  // Calculate total steps for progress bar
  const totalSteps = modelOrder.length;

  return (
    <div className="space-y-4">
      {/* User Question */}
      <div className="flex items-start gap-3">
        <Avatar className="mt-1">
          <AvatarFallback className="bg-slate-300">U</AvatarFallback>
        </Avatar>
        <div className="flex-1 prose max-w-none">
          <p className="text-lg">{userPrompt}</p>
        </div>
      </div>
      
      {/* Progress indicator */}
      {loading && (
        <div className="py-2 px-4">
          <div className="flex justify-between mb-1">
            <span className="text-sm text-slate-600">
              {t('discussingModels', { current: String(currentStep), total: String(totalSteps) })}
            </span>
            <span className="text-sm text-slate-600">
              {Math.round((currentStep / totalSteps) * 100)}%
            </span>
          </div>
          <Progress value={(currentStep / totalSteps) * 100} className="h-2" />
        </div>
      )}
      
      {/* Model Responses */}
      {modelOrder.map((model, index) => {
        const hasResponse = model in responses;
        // Only consider it the current step if it's actively streaming or loading without a response
        const isCurrentStep = (index === currentStep && loading && !hasResponse) || model === streamingModel;
        const isPending = index > currentStep && loading;
        
        return (
          <Card key={model} className={`relative overflow-hidden transition-all ${isCurrentStep ? 'border-blue-300 shadow-md' : ''}`}>
            {isCurrentStep && (
              <div className="absolute inset-0 bg-blue-50 opacity-20 animate-pulse" />
            )}
            
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <Avatar className="mt-1">
                  <AvatarFallback className={getModelColorClass(model)}>
                    {getModelInitials(model)}
                  </AvatarFallback>
                </Avatar>
                
                <div className="flex-1 prose max-w-none break-words">
                  <h4 className="mb-1 font-medium text-gray-700">{model.charAt(0).toUpperCase() + model.slice(1)}</h4>
                  
                  {/* Show loading state */}
                  {isCurrentStep && !hasResponse && (
                    <div className="flex items-center">
                      <div className="animate-pulse mr-2">
                        <Skeleton className="h-4 w-4 rounded-full" />
                      </div>
                      <span className="text-sm text-gray-500">{t('generating')}</span>
                    </div>
                  )}
                  
                  {/* Show streaming indicator */}
                  {model === streamingModel && hasResponse && (
                    <div className="inline-flex items-center mb-2 text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
                      <span className="mr-1">●</span> {t('streaming')}...
                    </div>
                  )}
                  
                  {/* Show pending state */}
                  {isPending && (
                    <div className="text-sm text-gray-400 italic">
                      {t('waitingForPreviousModel')}
                    </div>
                  )}
                  
                  {/* Show response content */}
                  {hasResponse && (
                    <div className="prose prose-slate max-w-none">
                      <Markdown rehypePlugins={[rehypeRaw]}>
                        {responses[model]}
                      </Markdown>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

export default DiscussionThread;
