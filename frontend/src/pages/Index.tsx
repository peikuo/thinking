
import React, { useEffect, useState } from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { AppProvider } from "@/contexts/AppContext";
import { ModeProvider } from "@/contexts/ModeContext";
import MainLayout from "@/components/MainLayout";
import { useApp } from "@/contexts/AppContext";
import { useParams, useNavigate } from "react-router-dom";
import { setupUrlChangeLogger } from "@/utils/testUrlNavigation";
import { Button } from "@/components/ui/button";

const IndexContent: React.FC = () => {
  const { conversationId } = useParams<{ conversationId: string }>();
  const navigate = useNavigate();
  const [showTestButton, setShowTestButton] = useState(false);
  
  const {
    conversations,
    activeConversationId,
    messages,
    createNewConversation,
    selectConversation,
    deleteConversation,
    renameConversation,
    clearAllConversations,
    sidebarOpen,
    toggleSidebar,
    loading,
    handleSubmitPrompt
  } = useApp();
  
  // Initialize URL change logger and test functions
  const [urlTester, setUrlTester] = useState<ReturnType<typeof setupUrlChangeLogger> | null>(null);
  
  // Set up URL change logger on mount
  useEffect(() => {
    // Show test button only in development
    if (process.env.NODE_ENV === 'development' || window.location.hostname === 'localhost') {
      setShowTestButton(true);
      setUrlTester(setupUrlChangeLogger());
    }
  }, []);
  
  // Handle URL-based conversation selection
  useEffect(() => {
    console.log('URL param conversationId:', conversationId);
    console.log('Available conversations:', conversations);
    console.log('Active conversation ID:', activeConversationId);
    
    if (conversationId) {
      // If a conversation ID is in the URL, select that conversation
      const conversation = conversations.find(c => c.id === conversationId);
      if (conversation) {
        console.log('Found conversation in URL, selecting:', conversationId);
        selectConversation(conversationId);
      } else {
        // If the conversation doesn't exist, redirect to home
        console.log('Conversation not found, redirecting to home');
        navigate('/');
      }
    }
  }, [conversationId, conversations, selectConversation, navigate, activeConversationId]);
  
  // Custom handlers that update the URL
  const handleNewConversation = () => {
    // createNewConversation returns the new ID
    const newId = createNewConversation();
    navigate('/');
    return newId;
  };
  
  const handleSelectConversation = (id: string) => {
    selectConversation(id);
    navigate(`/c/${id}`);
  };
  
  const handleDeleteConversation = (id: string) => {
    const isActive = id === activeConversationId;
    deleteConversation(id);
    if (isActive) {
      navigate('/');
    }
  };
  
  // Custom submit handler that updates the URL after first message
  const handleSubmit = async (prompt: string, selectedModels?: string[]) => {
    // First submit the prompt and get the conversation ID
    const resultConversationId = await handleSubmitPrompt(prompt, selectedModels);
    
    console.log('After submit - resultConversationId:', resultConversationId);
    console.log('After submit - activeConversationId:', activeConversationId);
    
    // If we're at the root URL and we have a conversation ID from the result,
    // update the URL to include the conversation ID
    if (!conversationId && resultConversationId) {
      console.log('Navigating to conversation URL:', `/c/${resultConversationId}`);
      navigate(`/c/${resultConversationId}`);
    }
  };

  // Function to test URL navigation
  const runUrlNavigationTest = async () => {
    if (urlTester) {
      // Test creating a new conversation and URL navigation
      await urlTester.testNewConversation(async (prompt) => {
        await handleSubmit(prompt);
      });
    }
  };
  
  return (
    <>
      <MainLayout
        conversations={conversations}
        activeConversationId={activeConversationId}
        messages={messages}
        loading={loading}
        sidebarOpen={sidebarOpen}
        onNewConversation={handleNewConversation}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
        onRenameConversation={renameConversation}
        onToggleSidebar={toggleSidebar}
        onSubmitPrompt={handleSubmit}
        clearAllConversations={clearAllConversations}
      />
      
      {/* Test button - only shown in development */}
      {showTestButton && (
        <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 1000 }}>
          <Button 
            onClick={runUrlNavigationTest}
            variant="outline"
            className="bg-blue-500 text-white hover:bg-blue-600"
          >
            Test URL Navigation
          </Button>
        </div>
      )}
    </>
  );
};

const Index: React.FC = () => {
  return (
    <SidebarProvider>
      <ModeProvider>
        <AppProvider>
          <IndexContent />
        </AppProvider>
      </ModeProvider>
    </SidebarProvider>
  );
};

export default Index;
