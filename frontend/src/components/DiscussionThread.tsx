import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { useLanguage } from '@/contexts/LanguageContext';
import Markdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
// Import KaTeX CSS
import 'katex/dist/katex.min.css';
// Import MermaidDiagram component
import MermaidDiagram from './MermaidDiagram';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { FileText } from 'lucide-react';
import { requestDiscussionSummary } from '@/lib/discuss-api';
import { useApiKeys } from '@/hooks/useApiKeys';

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
  const { apiKeys } = useApiKeys();
  
  // State for summary
  const [summaryContent, setSummaryContent] = useState<string>("");
  const [isSummarizing, setIsSummarizing] = useState<boolean>(false);
  const [showSummary, setShowSummary] = useState<boolean>(false);
  const [lastPromptSummarized, setLastPromptSummarized] = useState<string>("");
  
  // Function to generate summary
  const generateSummary = async () => {
    // Only generate summary if there are responses
    if (Object.keys(responses).length === 0) return;
    
    setIsSummarizing(true);
    setShowSummary(true);
    setSummaryContent("");
    
    try {
      await requestDiscussionSummary(
        userPrompt,
        responses,
        apiKeys,
        language,
        (content) => {
          setSummaryContent(content);
        }
      );
      
      // Track the prompt that was just summarized
      setLastPromptSummarized(userPrompt);
    } catch (error) {
      console.error("Error generating summary:", error);
      setSummaryContent(t('summaryError'));
    } finally {
      setIsSummarizing(false);
    }
  };
  
  // Determine the model order based on language
  const modelOrder = language === 'zh' 
    ? ['glm', 'doubao', 'deepseek', 'qwen'] 
    : ['openai', 'grok', 'qwen', 'deepseek'];
    
  // Calculate total steps for progress bar
  const totalSteps = modelOrder.length;
  
  // Calculate current progress more accurately
  // When loading, use currentStep (which is now properly updated in useDiscussMode)
  // When not loading, show all steps as completed
  const completedSteps = loading ? currentStep : Object.keys(responses).length || modelOrder.length;
  
  // Effect to handle summary visibility based on new prompts
  useEffect(() => {
    // If this is a new prompt (different from the last one we summarized)
    if (userPrompt !== lastPromptSummarized && lastPromptSummarized !== "") {
      // Hide the summary while the new responses are being generated
      setShowSummary(false);
    }
  }, [userPrompt, lastPromptSummarized]);
  
  // Separate effect to handle auto-summarization when responses are complete
  useEffect(() => {
    // When responses are complete for a new prompt, show the summary again
    if (!loading && 
        Object.keys(responses).length > 0 && 
        userPrompt !== lastPromptSummarized && 
        lastPromptSummarized !== "" && 
        summaryContent) {
      // Auto-generate a new summary for the updated conversation
      generateSummary();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, responses, userPrompt, lastPromptSummarized, summaryContent]);

  return (
    <div className="space-y-4">
      {/* User Question - Styled like chat mode */}
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-flow-primary/5 to-flow-secondary/5 backdrop-blur-sm p-6 rounded-2xl border border-white/20 shadow-sm">
          <p className="font-medium text-lg bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-2">{t('youAsked')}</p>
          <p className="text-gray-700 text-lg leading-relaxed">{userPrompt}</p>
        </div>
      </div>
      
      {/* Progress indicator */}
      {loading && (
        <div className="py-2 px-4">
          <div className="flex justify-between mb-1">
            <span className="text-sm text-slate-600">
              {t('discussingModels', { current: String(completedSteps), total: String(totalSteps) })}
            </span>
            <span className="text-sm text-slate-600">
              {Math.round((completedSteps / totalSteps) * 100)}%
            </span>
          </div>
          <Progress value={(completedSteps / totalSteps) * 100} className="h-2" />
        </div>
      )}
      
      {/* Model Responses */}
      {modelOrder.map((model, index) => {
        const hasResponse = model in responses;
        // Only consider it the current step if it's actively streaming or loading without a response
        const isCurrentStep = (index === currentStep && loading && !hasResponse) || model === streamingModel;
        // Only show pending state if the model is after the current step and doesn't have a response yet
        const isPending = index > currentStep && loading && !hasResponse;
        
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
                    <div className="prose prose-slate max-w-none prose-table:table-auto prose-table:border-collapse prose-td:border prose-td:border-gray-300 prose-td:p-2 prose-th:border prose-th:border-gray-300 prose-th:p-2">
                      <Markdown 
                        remarkPlugins={[remarkGfm, remarkMath]}
                        rehypePlugins={[rehypeRaw, rehypeKatex]}
                        components={{
                          code({ node, inline, className, children, ...props }) {
                            const match = /language-(\w+)/.exec(className || '');
                            const value = String(children).replace(/\n$/, '');
                            
                            if (match && match[1] === 'mermaid') {
                              return <MermaidDiagram chart={value} />;
                            }
                            
                            return <code className={className} {...props}>{children}</code>;
                          }
                        }}
                      >
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
      
      {/* Summary Button - Only show if there are responses and not currently loading */}
      {!loading && Object.keys(responses).length > 0 && (
        <div className="flex justify-center mt-4">
          <Button 
            variant="outline" 
            className="flex items-center gap-2"
            onClick={generateSummary}
            disabled={isSummarizing}
          >
            <FileText size={16} />
            {isSummarizing ? t('generatingSummary') : t('generateSummary')}
          </Button>
        </div>
      )}
      
      {/* Summary Display */}
      {showSummary && (
        <Card className={`mt-6 ${isSummarizing ? 'border-blue-300 shadow-md' : 'border-green-300'}`}>
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <Avatar className="mt-1">
                <AvatarFallback className="bg-emerald-500">S</AvatarFallback>
              </Avatar>
              
              <div className="flex-1 prose max-w-none break-words">
                <h4 className="mb-1 font-medium text-gray-700">{t('summary')}</h4>
                
                {/* Show loading state */}
                {isSummarizing && (
                  <div className="flex items-center mb-2">
                    <div className="animate-pulse mr-2">
                      <Skeleton className="h-4 w-4 rounded-full" />
                    </div>
                    <span className="text-sm text-gray-500">{t('generating')}</span>
                  </div>
                )}
                
                {/* Show summary content */}
                {summaryContent && (
                  <div className="prose prose-slate max-w-none prose-table:table-auto prose-table:border-collapse prose-td:border prose-td:border-gray-300 prose-td:p-2 prose-th:border prose-th:border-gray-300 prose-th:p-2">
                    <Markdown 
                      remarkPlugins={[remarkGfm, remarkMath]}
                      rehypePlugins={[rehypeRaw, rehypeKatex]}
                      components={{
                        code({ node, inline, className, children, ...props }) {
                          const match = /language-(\w+)/.exec(className || '');
                          const value = String(children).replace(/\n$/, '');
                          
                          if (match && match[1] === 'mermaid') {
                            return <MermaidDiagram chart={value} />;
                          }
                          
                          return <code className={className} {...props}>{children}</code>;
                        }
                      }}
                    >
                      {summaryContent}
                    </Markdown>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DiscussionThread;
