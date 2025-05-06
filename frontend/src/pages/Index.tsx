
import React from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { AppProvider } from "@/contexts/AppContext";
import { ModeProvider } from "@/contexts/ModeContext";
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
    handleSubmitPrompt
  } = useApp();

  return (
    <MainLayout
      conversations={conversations}
      activeConversationId={activeConversationId}
      messages={messages}
      loading={loading}
      sidebarOpen={sidebarOpen}
      onNewConversation={createNewConversation}
      onSelectConversation={selectConversation}
      onDeleteConversation={deleteConversation}
      onRenameConversation={renameConversation}
      onToggleSidebar={toggleSidebar}
      onSubmitPrompt={handleSubmitPrompt}
    />
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
