
import React, { useState, KeyboardEvent, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Keyboard } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Card } from "@/components/ui/card";

interface PromptInputProps {
  onSubmit: (prompt: string, selectedModels?: string[]) => void;
  loading: boolean;
}

const PromptInput: React.FC<PromptInputProps> = ({ onSubmit, loading }) => {
  const [prompt, setPrompt] = useState("");
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [cursorPosition, setCursorPosition] = useState<number | null>(null);
  const [mentionStartIndex, setMentionStartIndex] = useState<number | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const modelSelectorRef = useRef<HTMLDivElement>(null);
  const { t, language } = useLanguage();

  const availableModels = ['openai', 'grok', 'qwen', 'deepseek'];

  // Extract selected models from the prompt
  const extractSelectedModels = (text: string): string[] => {
    const modelMentions = text.match(/@(openai|grok|qwen|deepseek)\b/g);
    if (!modelMentions) return [];
    return modelMentions.map(mention => mention.substring(1)); // Remove @ symbol
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && !loading) {
      const selectedModels = extractSelectedModels(prompt.trim());
      const cleanPrompt = prompt.trim().replace(/@(openai|grok|qwen|deepseek)\b/g, '').trim();
      onSubmit(cleanPrompt, selectedModels.length > 0 ? selectedModels : undefined);
      setPrompt("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Close model selector on Escape
    if (e.key === 'Escape' && showModelSelector) {
      setShowModelSelector(false);
      return;
    }
    
    // Check for Enter (without Shift for new line)
    if (e.key === 'Enter') {
      if (showModelSelector) {
        e.preventDefault();
        return;
      }
      
      if (!e.shiftKey && !e.nativeEvent.isComposing) {
        e.preventDefault();
        if (prompt.trim() && !loading) {
          const selectedModels = extractSelectedModels(prompt.trim());
          const cleanPrompt = prompt.trim().replace(/@(openai|grok|qwen|deepseek)\b/g, '').trim();
          onSubmit(cleanPrompt, selectedModels.length > 0 ? selectedModels : undefined);
          setPrompt("");
        }
      }
    }
  };
  
  // Handle input changes to detect @ symbol
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setPrompt(newValue);
    
    const cursorPos = e.target.selectionStart;
    setCursorPosition(cursorPos);
    
    // Check if user just typed @
    if (newValue.charAt(cursorPos - 1) === '@') {
      setMentionStartIndex(cursorPos - 1);
      setShowModelSelector(true);
    } else if (mentionStartIndex !== null) {
      // Check if we're still in a mention context
      const textAfterMention = newValue.substring(mentionStartIndex, cursorPos);
      if (!textAfterMention.match(/^@[a-zA-Z]*$/)) {
        setShowModelSelector(false);
        setMentionStartIndex(null);
      }
    }
  };

  // Handle model selection
  const handleModelSelect = (model: string) => {
    if (mentionStartIndex !== null && textareaRef.current) {
      const beforeMention = prompt.substring(0, mentionStartIndex);
      const afterMention = prompt.substring(cursorPosition || mentionStartIndex);
      const newPrompt = `${beforeMention}@${model} ${afterMention}`;
      setPrompt(newPrompt);
      
      // Focus back on textarea and place cursor after the inserted model name
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.focus();
          const newCursorPos = mentionStartIndex + model.length + 2; // +2 for @ and space
          textareaRef.current.setSelectionRange(newCursorPos, newCursorPos);
        }
      }, 0);
    }
    setShowModelSelector(false);
    setMentionStartIndex(null);
  };
  
  // Close model selector when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modelSelectorRef.current && !modelSelectorRef.current.contains(event.target as Node) &&
          textareaRef.current && !textareaRef.current.contains(event.target as Node)) {
        setShowModelSelector(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <div className="relative">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Textarea
                ref={textareaRef}
                placeholder={t('inputPlaceholder')}
                value={prompt}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                className="min-h-24 resize-none rounded-lg border-gray-200 bg-white/50 backdrop-blur-sm shadow-sm transition-all duration-300 focus:border-[#10A37F]/50 focus:shadow-md text-lg"
                style={{ fontSize: '1.125rem' }}
                disabled={loading}
              />
            </TooltipTrigger>
            <TooltipContent side="top" className="bg-gray-800 text-white border-none">
              <div className="flex items-center gap-1">
                <Keyboard className="h-4 w-4" />
                <span>{t('shortcutTip')}</span>
              </div>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        
        {/* Model selector popup */}
        {showModelSelector && (
          <Card 
            ref={modelSelectorRef}
            className="absolute bottom-full mb-2 p-2 bg-white shadow-lg rounded-md border border-gray-200 w-64 z-50"
          >
            <div className="text-sm font-medium mb-2 text-gray-500">{t('selectModel')}</div>
            <div className="space-y-1">
              {availableModels.map(model => (
                <div 
                  key={model}
                  className="px-3 py-2 hover:bg-gray-100 rounded-md cursor-pointer flex items-center"
                  onClick={() => handleModelSelect(model)}
                >
                  <div className="w-2 h-2 rounded-full mr-2" 
                    style={{ backgroundColor: 
                      model === 'openai' ? '#10A37F' : 
                      model === 'grok' ? '#FF0080' : 
                      model === 'qwen' ? '#00BFFF' : 
                      '#6366F1' 
                    }} 
                  />
                  <span>{model}</span>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
      <Button 
        type="submit" 
        className="self-end rounded-md bg-[#10A37F] hover:bg-[#0E8D6E] text-white transition-all duration-300 hover:shadow-sm"
        disabled={loading || !prompt.trim()}
      >
        {loading ? t('processing') : t('send')}
        {!loading && <Send className="ml-2 h-4 w-4" />}
      </Button>
    </form>
  );
};

export default PromptInput;
