
import React from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { AppProvider } from "@/contexts/AppContext";
import MainLayout from "@/components/MainLayout";
import { useApp } from "@/contexts/AppContext";

const IndexContent: React.FC = () => {
  const {
    conversations,
    activeConversationId,
    messages,
    createNewConversation,
    selectConversation,
    deleteConversation,
    renameConversation,
    sidebarOpen,
    toggleSidebar,
    loading,
    conversationsLoading,
    handleSubmitPrompt
  } = useApp();

  return (
    <MainLayout
      conversations={conversations}
      activeConversationId={activeConversationId}
      messages={messages}
      loading={loading}
      sidebarOpen={sidebarOpen}
      conversationsLoading={conversationsLoading}
      onNewConversation={createNewConversation}
      onToggleSidebar={toggleSidebar}
      onSelectConversation={selectConversation}
      onDeleteConversation={deleteConversation}
      onRenameConversation={renameConversation}
      onSubmitPrompt={handleSubmitPrompt}
    />
  );
};

const Index: React.FC = () => {
  return (
    <SidebarProvider>
      <LanguageProvider>
        <AppProvider>
          <IndexContent />
        </AppProvider>
      </LanguageProvider>
    </SidebarProvider>
  );
};

export default Index;
