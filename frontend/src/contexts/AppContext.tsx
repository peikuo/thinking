import React, { createContext, useContext, ReactNode } from 'react';
import { useConversations, Conversation } from '@/hooks/useConversations';
import { useApiKeys, ApiKeys } from '@/hooks/useApiKeys';
import { useSidebar } from '@/hooks/useSidebar';
import { useModelApi } from '@/hooks/useModelApi';
import { useToast } from '@/components/ui/use-toast';
import { ConversationMessage, StreamingState } from '@/types/models';
import { useLanguage } from './LanguageContext';

interface AppContextType {
  // Conversations
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: ConversationMessage[];
  createNewConversation: () => void;
  selectConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  renameConversation: (id: string, newTitle: string) => void;
  
  // API Keys
  apiKeys: ApiKeys;
  saveApiKeys: (keys: ApiKeys) => void;
  
  // Sidebar
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  
  // API and Loading
  loading: boolean;
  summaryLoading: boolean;
  error: string | null;
  clearError: () => void;
  
  // Streaming State
  streamingContent: StreamingState;
  isStreaming: boolean;
  
  // Actions
  handleSubmitPrompt: (prompt: string) => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { t } = useLanguage();
  const { toast } = useToast();
  
  // Custom hooks
  const {
    conversations,
    activeConversationId,
    messages,
    createNewConversation,
    selectConversation,
    deleteConversation,
    renameConversation,
    addUserMessage,
    updateModelResponses,
    updateSummary
  } = useConversations();
  
  const { apiKeys, saveApiKeys } = useApiKeys();
  const { sidebarOpen, toggleSidebar } = useSidebar();
  const { loading, summaryLoading, error, streamingContent, isStreaming, queryModels, generateSummary, clearError } = useModelApi();
  
  // Main action to handle prompt submission
  const handleSubmitPrompt = async (prompt: string, selectedModels?: string[]) => {
    if (!prompt.trim()) return;
    
    // Get the active conversation to extract history before adding the new message
    const activeConversation = conversations.find(c => c.id === activeConversationId);
    const conversationHistory = activeConversation?.messages || [];
    
    // Add user message and get the conversation ID
    const conversationId = addUserMessage(prompt, selectedModels);
    
    try {
      // Always use streaming mode by default
      const result = await queryModels(prompt, apiKeys, true, selectedModels, conversationHistory);
      
      if (result) {
        // Update with model responses first (without summary)
        updateModelResponses(conversationId, result.modelResponses);
        
        // Only generate summary if we have more than one model response and no skipSummary flag
        if (result.modelResponses.length > 1 && !result.summary.skipSummary) {
          // Now request the summary separately
          const summary = await generateSummary(prompt, result.modelResponses, apiKeys);
          
          // Update just the summary after model responses are rendered
          updateSummary(conversationId, summary);
          
          toast({
            title: t('responsesGenerated'),
            description: selectedModels && selectedModels.length > 0 
              ? t('selectedModelsResponded') 
              : t('allModelsResponded'),
          });
        } else {
          // No summary needed for single model
          toast({
            title: t('responseGenerated'),
            description: t('modelResponded', { model: result.modelResponses[0].model }),
          });
        }
      } else {
        // Error already set in the hook
        toast({
          variant: "destructive",
          title: t('error'),
          description: t('failedToGetResponses'),
        });
      }
    } catch (err) {
      console.error("Error in handleSubmitPrompt:", err);
      toast({
        variant: "destructive",
        title: t('error'),
        description: t('failedToGetResponses'),
      });
    }
  };
  
  const value: AppContextType = {
    // Conversations
    conversations,
    activeConversationId,
    messages,
    createNewConversation,
    selectConversation,
    deleteConversation,
    renameConversation,
    
    // API Keys
    apiKeys,
    saveApiKeys,
    
    // Sidebar
    sidebarOpen,
    toggleSidebar,
    
    // API and Loading
    loading,
    summaryLoading,
    error,
    clearError,
    
    // Streaming State
    streamingContent,
    isStreaming,
    
    // Actions
    handleSubmitPrompt
  };
  
  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
