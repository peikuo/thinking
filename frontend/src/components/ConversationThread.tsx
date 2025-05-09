
import React, { memo, useMemo, useRef } from "react";
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
  const { t } = useLanguage();
  const { summaryLoading, streamingContent, isStreaming } = useApp();
  const threadEndRef = useRef<HTMLDivElement>(null);

  // Reference for the end of the thread (for potential future scroll functionality)

  // Helper function to render model responses based on layout
  const renderModelResponses = useMemo(() => {
    return (message: ConversationMessage, index: number, currentLayout: string, isLatestMessage: boolean) => {
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

            {/* Show summary for this message if it has one and multiple model responses */}
            {message.summary && message.modelResponses && message.modelResponses.length > 1 && (
              <div className="mt-8">
                <ComparisonSummary
                  summary={message.summary}
                  loading={summaryLoading && isLatestMessage}
                  streamingContent={isStreaming && isLatestMessage ? streamingContent.summary : undefined}
                  isStreaming={isStreaming && isLatestMessage}
                />
              </div>
            )}
          </>
        );
      } else if (currentLayout === 'grid') {
        // Grid layout - responses in a grid
        return (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            </div>

            {/* Show summary for this message if it has one and multiple model responses */}
            {message.summary && message.modelResponses && message.modelResponses.length > 1 && (
              <div className="mt-8">
                <ComparisonSummary
                  summary={message.summary}
                  loading={summaryLoading && isLatestMessage}
                  streamingContent={isStreaming && isLatestMessage ? streamingContent.summary : undefined}
                  isStreaming={isStreaming && isLatestMessage}
                />
              </div>
            )}
          </>
        );
      } else {
        // Comparison layout - side by side
        return (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            </div>

            {/* Show summary for this message if it has one and multiple model responses */}
            {message.summary && message.modelResponses && message.modelResponses.length > 1 && (
              <div className="mt-8">
                <ComparisonSummary
                  summary={message.summary}
                  loading={summaryLoading && isLatestMessage}
                  streamingContent={isStreaming && isLatestMessage ? streamingContent.summary : undefined}
                  isStreaming={isStreaming && isLatestMessage}
                />
              </div>
            )}
          </>
        );
      }
    };
  }, [layout, t, summaryLoading, streamingContent, isStreaming]);

  // Memoize the rendering of messages to prevent unnecessary re-renders
  const renderedContent = useMemo(() => {
    if (messages.length === 0) {
      return null;
    }

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
  }, [messages, renderModelResponses, layout, t]);

  return (
    <div className="space-y-10">
      {renderedContent}
      <div ref={threadEndRef} />
    </div>
  );
});

export default ConversationThread;
