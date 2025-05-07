import { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { ConversationMessage, ModelResponse } from '@/types/models';

export interface Conversation {
  id: string;
  title: string;
  messages: ConversationMessage[];
  timestamp: number; // Unix timestamp in milliseconds
}

// Helper function to generate a title from the first user message
const generateTitle = (content: string): string => {
  if (!content || content.trim() === '') {
    return "New Conversation";
  }
  
  // Truncate to first 30 chars or less
  const maxLength = 30;
  const trimmedContent = content.trim();
  if (trimmedContent.length <= maxLength) return trimmedContent;
  return trimmedContent.substring(0, maxLength) + "...";
};

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);

  // Load conversations from localStorage on mount
  useEffect(() => {
    const savedConversations = localStorage.getItem('ai-comparison-conversations');
    if (savedConversations) {
      try {
        let parsed = JSON.parse(savedConversations);
        
        // Add timestamps to any existing conversations that don't have them
        parsed = parsed.map((conv: Conversation, index: number) => {
          if (!conv.timestamp) {
            // If no timestamp, create one based on index (older conversations get older timestamps)
            const now = Date.now();
            const daysAgo = index * 1; // Each conversation is 1 day older than the previous
            return {
              ...conv,
              timestamp: now - (daysAgo * 86400000) // 86400000 = 1 day in milliseconds
            };
          }
          return conv;
        });
        
        // Check if there's any streaming content saved
        const savedStreamingContent = localStorage.getItem('thinking-streaming-content');
        if (savedStreamingContent) {
          try {
            const streamingData = JSON.parse(savedStreamingContent);
            
            // Find the most recent conversation with an assistant message
            if (parsed.length > 0) {
              const mostRecentConv = parsed[0];
              if (mostRecentConv.messages && mostRecentConv.messages.length > 0) {
                // Get the last assistant message
                const lastAssistantIndex = mostRecentConv.messages.findIndex(
                  (msg: ConversationMessage) => msg.role === 'assistant'
                );
                
                if (lastAssistantIndex !== -1) {
                  // Update the model responses with streaming content
                  const assistantMsg = mostRecentConv.messages[lastAssistantIndex];
                  if (assistantMsg.modelResponses) {
                    // Important: Reset loading state for ALL model responses
                    assistantMsg.modelResponses = assistantMsg.modelResponses.map(
                      (response: ModelResponse) => {
                        const modelKey = response.model as keyof typeof streamingData;
                        // If we have streaming content for this model, use it
                        if (streamingData[modelKey] && streamingData[modelKey].length > 0) {
                          return {
                            ...response,
                            content: streamingData[modelKey],
                            loading: false
                          };
                        }
                        // Otherwise, if it's still in loading state but has no content after refresh,
                        // assume the request failed and show an empty response instead of perpetual loading
                        else if (response.loading) {
                          return {
                            ...response,
                            loading: false,
                            content: response.content || "No response received. Please try again."
                          };
                        }
                        return response;
                      }
                    );
                    
                    // Update the conversation with the updated model responses
                    parsed[0] = {
                      ...mostRecentConv,
                      messages: [
                        ...mostRecentConv.messages.slice(0, lastAssistantIndex),
                        assistantMsg,
                        ...mostRecentConv.messages.slice(lastAssistantIndex + 1)
                      ]
                    };
                  }
                }
              }
            }
          } catch (e) {
            console.error("Failed to parse streaming content:", e);
          }
        }
        
        setConversations(parsed);
        
        // If there are conversations, set the most recent one as active
        if (parsed.length > 0) {
          // Sort by timestamp (newest first) and get the first one
          const sorted = [...parsed].sort((a, b) => b.timestamp - a.timestamp);
          setActiveConversationId(sorted[0].id);
        }
      } catch (e) {
        console.error("Failed to parse saved conversations:", e);
        setConversations([]);
      }
    }
  }, []);
  
  // Save conversations to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('ai-comparison-conversations', JSON.stringify(conversations));
  }, [conversations]);
  
  // Get current conversation messages
  const activeConversation = activeConversationId 
    ? conversations.find(c => c.id === activeConversationId)
    : null;
  
  const messages = activeConversation?.messages || [];
  
  const createNewConversation = useCallback(() => {
    const newId = uuidv4();
    const timestamp = Date.now();
    
    const newConversation = {
      id: newId,
      title: "New Conversation",
      messages: [],
      timestamp: timestamp
    };
    
    // Update state with the new conversation
    setConversations(prevConversations => {
      const updatedConversations = [newConversation, ...prevConversations];
      // Immediately persist to localStorage
      localStorage.setItem('ai-comparison-conversations', JSON.stringify(updatedConversations));
      return updatedConversations;
    });
    
    // Set this as the active conversation
    setActiveConversationId(newId);
    
    return newId;
  }, []);
  
  const selectConversation = useCallback((id: string) => {
    // Set the active conversation ID
    setActiveConversationId(id);
    
    // Find the conversation to check if it's a discuss mode conversation
    const conversation = conversations.find(c => c.id === id);
    
    // If the conversation exists and has the isDiscussMode property
    if (conversation) {
      // Get the current mode from localStorage
      const currentMode = localStorage.getItem('thinking-mode') || 'chat';
      
      // Check if we need to switch modes
      if (conversation.isDiscussMode && currentMode !== 'discuss') {
        // Switch to discuss mode
        localStorage.setItem('thinking-mode', 'discuss');
        // Reload the discuss mode history if needed
        if (conversation.messages && conversation.messages.length > 0) {
          // Find user messages to use as the prompt
          const userMessages = conversation.messages.filter(msg => msg.role === 'user');
          if (userMessages.length > 0) {
            const firstUserMsg = userMessages[0].content;
            // Save the prompt to localStorage for discuss mode
            localStorage.setItem('thinking-discuss-prompt', firstUserMsg);
            
            // If there are assistant responses, save them to discuss responses
            const assistantMessages = conversation.messages.filter(msg => msg.role === 'assistant');
            if (assistantMessages.length > 0 && assistantMessages[0].modelResponses) {
              // Convert modelResponses to the format expected by discuss mode
              const discussResponses: Record<string, string> = {};
              assistantMessages[0].modelResponses.forEach(response => {
                discussResponses[response.model] = response.content;
              });
              localStorage.setItem('thinking-discuss-responses', JSON.stringify(discussResponses));
            }
          }
        }
      } else if (!conversation.isDiscussMode && currentMode !== 'chat') {
        // Switch to chat mode
        localStorage.setItem('thinking-mode', 'chat');
      }
      
      // Force a page reload to apply the mode change
      // This is a simple way to ensure the UI updates correctly
      window.location.reload();
    }
  }, [conversations]);
  
  const deleteConversation = useCallback((id: string) => {
    setConversations(prev => {
      const filtered = prev.filter(c => c.id !== id);
      
      // If we're deleting the active conversation, select the next one
      if (id === activeConversationId && filtered.length > 0) {
        setActiveConversationId(filtered[0].id);
      } else if (filtered.length === 0) {
        setActiveConversationId(null);
      }
      
      return filtered;
    });
  }, [activeConversationId]);
  
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
    
    // Import language from window.localStorage using the correct key
    // The LanguageContext uses 'ai-comparison-language' as the key
    const storedLanguage = window.localStorage.getItem('ai-comparison-language') || 'en';
    
    // Determine which models to show based on language and selected models
    const defaultModels = storedLanguage === 'zh'
      ? ["deepseek", "qwen", "doubao", "glm"]
      : ["openai", "grok", "qwen", "deepseek"];
    
    // Use selected models if provided, otherwise use language-specific defaults
    const modelsToShow = selectedModels || defaultModels;
    
    console.log(`useConversations - Using models for ${storedLanguage} locale:`, modelsToShow);
    
    // Create placeholders for model responses (only for selected models)
    const loadingResponses: ModelResponse[] = [];
    
    // Define all possible models
    const allModels = ['openai', 'grok', 'qwen', 'deepseek', 'doubao', 'glm'] as const;
    
    // Create loading placeholders for all selected models
    allModels.forEach(model => {
      if (modelsToShow.includes(model)) {
        loadingResponses.push({ 
          model: model as 'openai' | 'grok' | 'qwen' | 'deepseek' | 'doubao' | 'glm', 
          content: "", 
          loading: true 
        });
      }
    });
    
    const assistantMessage: ConversationMessage = {
      role: "assistant",
      content: "",
      modelResponses: loadingResponses,
      selectedModels: modelsToShow
    };
    
    // Update the conversation with the assistant message
    setConversations(prev => {
      const updated = [...prev];
      const index = updated.findIndex(c => c.id === currentConversationId);
      if (index !== -1) {
        // If this is the first message, update the title
        if (updated[index].messages.length === 0) {
          updated[index].title = generateTitle(prompt);
        }
        
        // Add the user message
        updated[index].messages.push(userMessage);
        
        // Add the assistant message with model responses
        updated[index].messages.push(assistantMessage);
        
        // Update timestamp to current time when adding new messages
        updated[index].timestamp = Date.now();
      }
      return updated;
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
  
  // Update just the summary after model responses are rendered
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
  
  // Remove the last assistant message when an API call fails
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
  
  // Clear all conversations and create a new one
  const clearAllConversations = useCallback(() => {
    // Create a new conversation
    const newId = uuidv4();
    const newConversation = {
      id: newId,
      title: "New Conversation",
      messages: [],
      timestamp: Date.now()
    };
    
    // Clear all conversations and add the new one
    setConversations([newConversation]);
    
    // Set this as the active conversation
    setActiveConversationId(newId);
    
    // Persist to localStorage
    localStorage.setItem('ai-comparison-conversations', JSON.stringify([newConversation]));
    
    return newId;
  }, []);
  
  return {
    conversations,
    activeConversationId,
    messages,
    createNewConversation,
    selectConversation,
    deleteConversation,
    renameConversation,
    addUserMessage,
    updateModelResponses,
    updateSummary,
    removeLastAssistantMessage,
    clearAllConversations
  };
}
