import { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { ConversationMessage, ModelResponse } from '@/types/models';

export interface Conversation {
  id: string;
  title: string;
  messages: ConversationMessage[];
}

// Helper function to generate a title from the first user message
const generateTitle = (content: string): string => {
  // Truncate to first 30 chars or less
  const maxLength = 30;
  if (content.length <= maxLength) return content;
  return content.substring(0, maxLength) + "...";
};

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);

  // Load conversations from localStorage on mount
  useEffect(() => {
    const savedConversations = localStorage.getItem('ai-comparison-conversations');
    if (savedConversations) {
      try {
        const parsed = JSON.parse(savedConversations);
        setConversations(parsed);
        
        // Set the active conversation to the most recent one if it exists
        if (parsed.length > 0) {
          setActiveConversationId(parsed[0].id);
        }
      } catch (e) {
        console.error('Failed to parse saved conversations', e);
      }
    }
  }, []);

  // Save conversations to localStorage when they change
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('ai-comparison-conversations', JSON.stringify(conversations));
    }
  }, [conversations]);

  // Get current conversation messages
  const activeConversation = activeConversationId 
    ? conversations.find(c => c.id === activeConversationId)
    : null;
  
  const messages = activeConversation?.messages || [];

  const createNewConversation = useCallback(() => {
    const newId = uuidv4();
    setConversations(prev => [{
      id: newId,
      title: "New Conversation",
      messages: []
    }, ...prev]);
    setActiveConversationId(newId);
    return newId;
  }, []);

  const selectConversation = useCallback((id: string) => {
    setActiveConversationId(id);
  }, []);

  const deleteConversation = useCallback((id: string) => {
    setConversations(prev => prev.filter(c => c.id !== id));
    
    // If we deleted the active conversation, select the next one
    if (activeConversationId === id) {
      const remainingConversations = conversations.filter(c => c.id !== id);
      if (remainingConversations.length > 0) {
        setActiveConversationId(remainingConversations[0].id);
      } else {
        setActiveConversationId(null);
      }
    }
  }, [activeConversationId, conversations]);

  const addUserMessage = useCallback((prompt: string, selectedModels?: string[]) => {
    let currentConversationId = activeConversationId;
    
    // Create a new conversation if none is active
    if (!currentConversationId) {
      currentConversationId = createNewConversation();
    }
    
    // Add user message
    const userMessage: ConversationMessage = {
      role: "user",
      content: prompt
    };
    
    // Determine which models to show based on selected models
    const modelsToShow = selectedModels || ["openai", "grok", "qwen", "deepseek"];
    
    // Create placeholders for model responses (only for selected models)
    const loadingResponses: ModelResponse[] = [];
    
    if (modelsToShow.includes("openai")) {
      loadingResponses.push({ model: "openai", content: "", loading: true });
    }
    
    if (modelsToShow.includes("grok")) {
      loadingResponses.push({ model: "grok", content: "", loading: true });
    }
    
    if (modelsToShow.includes("qwen")) {
      loadingResponses.push({ model: "qwen", content: "", loading: true });
    }
    
    if (modelsToShow.includes("deepseek")) {
      loadingResponses.push({ model: "deepseek", content: "", loading: true });
    }
    
    const assistantMessage: ConversationMessage = {
      role: "assistant",
      content: "",
      modelResponses: loadingResponses,
      selectedModels: modelsToShow
    };
    
    // Update conversation with user message and loading state
    setConversations(prev => {
      return prev.map(conv => {
        if (conv.id === currentConversationId) {
          const isFirstMessage = conv.messages.length === 0;
          const newMessages = [...conv.messages, userMessage, assistantMessage];
          return {
            ...conv,
            title: isFirstMessage ? generateTitle(prompt) : conv.title,
            messages: newMessages
          };
        }
        return conv;
      });
    });
    
    return currentConversationId;
  }, [activeConversationId, createNewConversation]);

  const updateModelResponses = useCallback((
    conversationId: string,
    modelResponses: ModelResponse[]
  ) => {
    setConversations(prev => {
      return prev.map(conv => {
        if (conv.id === conversationId) {
          const conversationMessages = [...conv.messages];
          const lastMessageIndex = conversationMessages.length - 1;
          
          if (lastMessageIndex >= 0 && conversationMessages[lastMessageIndex].role === "assistant") {
            conversationMessages[lastMessageIndex] = {
              ...conversationMessages[lastMessageIndex],
              modelResponses: modelResponses
            };
          }
          
          return {
            ...conv,
            messages: conversationMessages
          };
        }
        return conv;
      });
    });
  }, []);

  // New function to update just the summary after model responses are rendered
  const updateSummary = useCallback((
    conversationId: string,
    summary: any
  ) => {
    setConversations(prev => {
      return prev.map(conv => {
        if (conv.id === conversationId) {
          const conversationMessages = [...conv.messages];
          const lastMessageIndex = conversationMessages.length - 1;
          
          if (lastMessageIndex >= 0 && conversationMessages[lastMessageIndex].role === "assistant") {
            conversationMessages[lastMessageIndex] = {
              ...conversationMessages[lastMessageIndex],
              summary: summary
            };
          }
          
          return {
            ...conv,
            messages: conversationMessages
          };
        }
        return conv;
      });
    });
  }, []);

  // Add function to rename a conversation
  const renameConversation = useCallback((id: string, newTitle: string) => {
    setConversations(prev => {
      return prev.map(conv => {
        if (conv.id === id) {
          return {
            ...conv,
            title: newTitle
          };
        }
        return conv;
      });
    });
  }, []);

  // New function to remove the last assistant message when an API call fails
  const removeLastAssistantMessage = useCallback((conversationId: string) => {
    setConversations(prev => {
      return prev.map(conv => {
        if (conv.id === conversationId) {
          // Get all messages except the last assistant message
          const messages = [...conv.messages];
          
          // Check if the last message is an assistant message
          if (messages.length > 0 && messages[messages.length - 1].role === "assistant") {
            // Remove the last message (assistant)
            messages.pop();
          }
          
          return {
            ...conv,
            messages
          };
        }
        return conv;
      });
    });
  }, []);

  return {
    conversations,
    activeConversationId,
    messages,
    createNewConversation,
    selectConversation,
    deleteConversation,
    addUserMessage,
    updateModelResponses,
    updateSummary,
    renameConversation,
    removeLastAssistantMessage
  };
}
