
import React, { memo, useMemo, useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ModelResponse } from "@/types/models";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw"; // Import rehype-raw to parse HTML tags
import WaveLoadingAnimation from "./WaveLoadingAnimation";
import { Separator } from "@/components/ui/separator";

interface ModelResponseCardProps {
  response: ModelResponse;
  streamingContent?: string;
  isStreaming?: boolean;
}

const modelNames = {
  openai: "OpenAI",
  grok: "Grok",
  qwen: "Qwen",
  deepseek: "DeepSeek",
  doubao: "Doubao",
  glm: "GLM",
  summary: "Summary"
};

const ModelResponseCard = memo(({ response, streamingContent, isStreaming }: ModelResponseCardProps) => {
  const { model, content, loading, error } = response;
  
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
      setDisplayedContent(content);
      previousStreamingContent.current = "";
    }
  }, [isStreaming, streamingContent, content, isTyping, displayedContent]);
  
  // Determine what content to display
  const memoizedDisplayContent = useMemo(() => {
    return isStreaming ? displayedContent : content;
  }, [isStreaming, displayedContent, content]);
  
  // Memoize markdown components to prevent unnecessary re-renders
  const markdownComponents = useMemo(() => ({
    h1: ({ children }) => <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-4">{children}</h1>,
    h2: ({ children }) => <h2 className="text-xl font-semibold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-3">{children}</h2>,
    h3: ({ children }) => <h3 className="text-lg font-semibold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-2">{children}</h3>,
    h4: ({ children }) => <h4 className="text-base font-semibold mb-2">{children}</h4>,
    p: ({ children }) => <p className="text-base mb-3 leading-relaxed">{children}</p>,
    ul: ({ children }) => <ul className="list-disc pl-5 mb-4">{children}</ul>,
    ol: ({ children }) => <ol className="list-decimal pl-5 mb-4">{children}</ol>,
    li: ({ children }) => <li className="mb-1 text-base">{children}</li>,
    blockquote: ({ children }) => <blockquote className="border-l-4 border-flow-primary pl-4 italic my-4">{children}</blockquote>,
    hr: () => <Separator className="bg-gradient-to-r from-transparent via-gray-200 to-transparent opacity-50 my-4" />,
    code: ({ inline, className, children, ...props }: any) => {
      if (inline) {
        return <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props}>{children}</code>;
      }
      return (
        <pre className="bg-gray-100 p-4 rounded-md overflow-auto my-4">
          <code className={className} {...props}>{children}</code>
        </pre>
      );
    },
    pre: ({ children }: any) => {
      // Special handling for pre blocks to preserve ASCII art and diagrams
      return <div className="whitespace-pre overflow-x-auto font-mono text-sm bg-gray-100 p-4 rounded-md my-4">{children}</div>;
    },
    table: ({ children }) => <div className="overflow-x-auto my-4 w-full"><table className="w-full border-collapse border-2 border-gray-300 table-auto">{children}</table></div>,
    thead: ({ children }) => <thead className="bg-gray-100">{children}</thead>,
    tbody: ({ children }) => <tbody className="divide-y divide-gray-300">{children}</tbody>,
    tr: ({ children }) => <tr className="border-b border-gray-300 hover:bg-gray-50">{children}</tr>,
    th: ({ children }) => <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-r border-gray-300 last:border-r-0 bg-gray-100">{children}</th>,
    td: ({ children }) => <td className="px-4 py-3 text-sm whitespace-normal break-words border-r border-gray-300 last:border-r-0">{children}</td>
  }), []);
  
  return (
    <Card className={cn(
      "model-response-container",
      `${model}-response`,
      "bg-white shadow-sm" // Use solid background instead of backdrop blur for consistency
    )}>
      <CardHeader className="pb-2">
        <CardTitle className="text-xl flex items-center">
          <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: `var(--model-${model})` }} />
          <span className="text-gray-800">
            {modelNames[model]}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading && !isStreaming ? (
          <div className="space-y-3">
            <WaveLoadingAnimation color={`var(--model-${model})`} text={`${modelNames[model]} is thinking...`} />
            <div className="space-y-3 mt-3">
              <div className="h-4 bg-gray-200 rounded animate-pulse w-[95%]"></div>
              <div className="h-4 bg-gray-200 rounded animate-pulse delay-75 w-[90%]"></div>
              <div className="h-4 bg-gray-200 rounded animate-pulse delay-150 w-full"></div>
              <div className="h-4 bg-gray-200 rounded animate-pulse delay-225 w-[85%]"></div>
              <div className="h-4 bg-gray-200 rounded animate-pulse delay-300 w-[92%]"></div>
            </div>
          </div>
        ) : error ? (
          <div className="text-destructive font-medium">
            Error: {error}
          </div>
        ) : (
          <div className="prose prose-base max-w-none dark:prose-invert prose-table:overflow-x-auto prose-table:w-full prose-img:rounded-md prose-img:mx-auto markdown-body">
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
              components={markdownComponents}
            >
              {memoizedDisplayContent}
            </ReactMarkdown>
          </div>
        )}
      </CardContent>
    </Card>
  );
});

export default ModelResponseCard;
