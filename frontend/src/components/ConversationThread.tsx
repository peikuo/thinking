
import React, { memo, useMemo } from "react";
import { ConversationMessage } from "@/types/models";
import ModelResponseCard from "./ModelResponseCard";
import ComparisonSummary from "./ComparisonSummary";
import { useLayout } from "@/contexts/LayoutContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { useApp } from "@/contexts/AppContext";
import { StreamingState } from "@/types/models";

interface ConversationThreadProps {
  messages: ConversationMessage[];
}

const ConversationThread = memo(({ messages }: ConversationThreadProps) => {
  const { layout } = useLayout();
  const { t, language } = useLanguage();
  const { summaryLoading, streamingContent, isStreaming } = useApp();
  const threadEndRef = React.useRef<HTMLDivElement>(null);
  
  // Auto-scroll to the latest message when messages change
  React.useEffect(() => {
    if (messages.length > 0) {
      threadEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages.length]);
  
  // Debug logging for streaming state
  React.useEffect(() => {
    if (isStreaming) {
      console.log('ConversationThread - isStreaming:', isStreaming);
      console.log('ConversationThread - streamingContent:', streamingContent);
    }
  }, [isStreaming, streamingContent]);
  
  // Return early if no messages
  if (messages.length === 0) {
    return null;
  }
  
  // Helper function to render model responses based on layout
  const renderModelResponses = (message: ConversationMessage, index: number, currentLayout: string, isLatestMessage: boolean) => {

    if (currentLayout === 'default') {
      // Default layout - each model response in its own row
      return (
        <>
          {message.modelResponses?.map((response, i) => {
            // Skip rendering if this message has selectedModels and this model is not in the list
            if (message.selectedModels && !message.selectedModels.includes(response.model)) {
              return null;
            }
            
            return (
              <ModelResponseCard 
                key={`${index}-${i}`} 
                response={response} 
                streamingContent={isStreaming && isLatestMessage ? streamingContent[response.model as keyof StreamingState] : undefined}
                isStreaming={isStreaming && isLatestMessage}
              />
            );
          })}
          
          {message.summary ? (
            <ComparisonSummary 
              summary={message.summary} 
              streamingContent={isStreaming && isLatestMessage ? streamingContent.summary : undefined}
              isStreaming={isStreaming && isLatestMessage}
            />
          ) : summaryLoading && (
            <ComparisonSummary 
              summary={{ content: "" }} 
              loading={true}
              streamingContent={isStreaming && isLatestMessage ? streamingContent.summary : undefined}
              isStreaming={isStreaming && isLatestMessage}
            />
          )}
        </>
      );
    } else {
      // Compact layout - 2 models per row, summary in its own row
      // For compact layout, show all models in a grid without filtering by type
      console.log('ConversationThread - Language:', language);
      console.log('ConversationThread - Available responses:', message.modelResponses?.map(r => r.model));
      
      return (
        <>
          {message.modelResponses && message.modelResponses.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Show all models in a grid */}
              {message.modelResponses.map((response, i) => (
                <ModelResponseCard 
                  key={`${index}-model-${i}`} 
                  response={response} 
                  streamingContent={isStreaming && isLatestMessage ? streamingContent[response.model as keyof StreamingState] : undefined}
                  isStreaming={isStreaming && isLatestMessage}
                />
              ))}
            </div>
          )}
          
          {/* Third row: Summary */}
          {message.summary ? (
            <div className="mt-4">
              <ComparisonSummary 
                summary={message.summary} 
                streamingContent={isStreaming && isLatestMessage ? streamingContent.summary : undefined}
                isStreaming={isStreaming && isLatestMessage}
              />
            </div>
          ) : summaryLoading && (
            <div className="mt-4">
              <ComparisonSummary 
                summary={{ content: "" }} 
                loading={true}
                streamingContent={isStreaming && isLatestMessage ? streamingContent.summary : undefined}
                isStreaming={isStreaming && isLatestMessage}
              />
            </div>
          )}
        </>
      );
    }
  };
  
  // Memoize the rendering of messages to prevent unnecessary re-renders
  const renderedMessages = useMemo(() => {
    // Find the last message with model responses to only apply streaming to it
    const lastModelResponseIndex = messages.map((msg, i) => ({ msg, i }))
      .filter(item => item.msg.modelResponses && item.msg.modelResponses.length > 0)
      .pop()?.i;
      
    return messages.map((message, index) => {
      if (message.role === "user") {
        return (
          <div key={`user-${index}`} className="space-y-6">
            <div className="bg-gradient-to-r from-flow-primary/5 to-flow-secondary/5 backdrop-blur-sm p-6 rounded-2xl border border-white/20 shadow-sm">
              <p className="font-medium text-lg bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-2">{t('youAsked')}</p>
              <p className="text-gray-700 text-lg leading-relaxed">{message.content}</p>
            </div>
          </div>
        );
      } else {
        return (
          <div key={`assistant-${index}`} className="space-y-6">
            {renderModelResponses(message, index, layout, index === lastModelResponseIndex)}
          </div>
        );
      }
    });
  }, [messages, layout, t, summaryLoading, streamingContent, isStreaming]);
  
  return (
    <div className="space-y-10">
      {renderedMessages}
      <div ref={threadEndRef} />
    </div>
  );
});

export default ConversationThread;
