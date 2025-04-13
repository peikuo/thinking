
import React, { useMemo, useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ComparisonSummary as Summary } from "@/types/models";
import { Separator } from "@/components/ui/separator";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import WaveLoadingAnimation from "./WaveLoadingAnimation";
import { useLanguage } from "@/contexts/LanguageContext";

interface ComparisonSummaryProps {
  summary: Summary;
  loading?: boolean;
  streamingContent?: string;
  isStreaming?: boolean;
}

const ComparisonSummary = React.memo(({ summary, loading, streamingContent, isStreaming }: ComparisonSummaryProps) => {
  const { t } = useLanguage();
  
  // Debug logging
  React.useEffect(() => {
    console.log('ComparisonSummary - Props:', { 
      isStreaming, 
      hasStreamingContent: !!streamingContent, 
      streamingContent,
      summaryContent: summary.content,
      loading
    });
  }, [isStreaming, streamingContent, summary.content, loading]);
  
  // State for the typing effect
  const [displayedContent, setDisplayedContent] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const previousStreamingContent = useRef("");
  
  // Typing effect configuration
  const typingSpeed = 10; // ms per character (adjust for faster/slower typing)
  
  // Handle typing effect for streaming content
  useEffect(() => {
    if (isStreaming && streamingContent && streamingContent !== previousStreamingContent.current) {
      // New content received from streaming
      const newContent = streamingContent;
      previousStreamingContent.current = newContent;
      
      // If not currently typing, start the typing effect
      if (!isTyping) {
        setIsTyping(true);
        let currentLength = displayedContent.length;
        
        // Function to add one character at a time
        const typeNextChar = () => {
          if (currentLength < newContent.length) {
            setDisplayedContent(newContent.substring(0, currentLength + 1));
            currentLength++;
            setTimeout(typeNextChar, typingSpeed);
          } else {
            setIsTyping(false);
          }
        };
        
        // Start typing
        typeNextChar();
      }
    } else if (!isStreaming) {
      // Not streaming, show the full content immediately
      setDisplayedContent(summary.content);
      previousStreamingContent.current = "";
    }
  }, [isStreaming, streamingContent, summary.content, isTyping, displayedContent]);
  
  // Determine what content to display
  const displayContent = useMemo(() => {
    if (isStreaming) {
      console.log('ComparisonSummary - Using typed content:', displayedContent);
      return displayedContent;
    }
    console.log('ComparisonSummary - Using summary content:', summary.content);
    return summary.content;
  }, [isStreaming, displayedContent, summary.content]);
  
  // Only show a light animation if loading and not streaming
  // This allows streaming content to be visible immediately
  if (loading && !isStreaming && !streamingContent) {
    return (
      <Card className="model-response-container summary-response bg-white shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg flex items-center">
            <div className="w-3 h-3 rounded-full mr-2 bg-model-summary animate-pulse" />
            <span className="bg-gradient-to-r from-flow-primary to-flow-secondary bg-clip-text text-transparent">
              {t('aiResponseComparison')}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="flex space-x-3">
              <div className="w-2 h-2 rounded-full bg-model-summary animate-pulse"></div>
              <div className="w-2 h-2 rounded-full bg-model-summary animate-pulse delay-150"></div>
              <div className="w-2 h-2 rounded-full bg-model-summary animate-pulse delay-300"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="model-response-container summary-response bg-white shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-xl flex items-center">
          <div className={`w-3 h-3 rounded-full mr-2 ${isStreaming ? 'bg-green-500 animate-pulse' : 'bg-model-summary'}`} />
          <span className="bg-gradient-to-r from-flow-primary to-flow-secondary bg-clip-text text-transparent">
            {t('aiResponseComparison')}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="prose prose-base max-w-none dark:prose-invert prose-table:overflow-x-auto prose-table:w-full prose-img:rounded-md prose-img:mx-auto">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({ children }) => <h1 className="text-2xl font-bold bg-gradient-to-r from-flow-primary to-flow-secondary bg-clip-text text-transparent mb-4">{children}</h1>,
              h2: ({ children }) => <h2 className="text-xl font-semibold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-3">{children}</h2>,
              h3: ({ children }) => <h3 className="text-lg font-semibold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-2">{children}</h3>,
              h4: ({ children }) => <h4 className="text-base font-semibold mb-2">{children}</h4>,
              p: ({ children }) => <p className="text-base mb-3 leading-relaxed">{children}</p>,
              ul: ({ children }) => <ul className="list-disc pl-5 mb-4">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal pl-5 mb-4">{children}</ol>,
              li: ({ children }) => <li className="mb-1 text-base">{children}</li>,
              code: ({ inline, className, children, ...props }: any) => {
                if (inline) {
                  return <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props}>{children}</code>;
                }
                return <code className={className} {...props}>{children}</code>;
              },
              blockquote: ({ children }) => <blockquote className="border-l-4 border-flow-primary pl-4 italic my-4">{children}</blockquote>,
              hr: () => <Separator className="bg-gradient-to-r from-transparent via-gray-200 to-transparent opacity-50 my-4" />,
              table: ({ children }) => <div className="overflow-x-auto my-4 w-full"><table className="w-full border-collapse">{children}</table></div>,
              thead: ({ children }) => <thead className="bg-gray-50">{children}</thead>,
              tbody: ({ children }) => <tbody className="divide-y divide-gray-200">{children}</tbody>,
              tr: ({ children }) => <tr className="hover:bg-gray-50">{children}</tr>,
              th: ({ children }) => <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{children}</th>,
              td: ({ children }) => <td className="px-4 py-3 text-base whitespace-normal break-words">{children}</td>
            }}
          >
            {displayContent}
          </ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  );
});

export default ComparisonSummary;
