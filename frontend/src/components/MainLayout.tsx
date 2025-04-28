import React from 'react';
import AppHeader from '@/components/AppHeader';
import ConversationHistorySidebar from '@/components/ConversationHistorySidebar';
import MainContent from '@/components/MainContent';
import ScrollButton from '@/components/ScrollButton';
import ModeSwitch from '@/components/ModeSwitch';
import { Conversation } from '@/hooks/useConversations';
import { ConversationMessage } from '@/types/models';
import { useMode } from '@/contexts/ModeContext';
import { useLanguage } from '@/contexts/LanguageContext';

interface MainLayoutProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: ConversationMessage[];
  loading: boolean;
  sidebarOpen: boolean;
  onNewConversation: () => void;
  onToggleSidebar: () => void;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
  onRenameConversation: (id: string, newTitle: string) => void;
  onSubmitPrompt: (prompt: string) => void;
}

const MainLayout: React.FC<MainLayoutProps> = ({
  conversations,
  activeConversationId,
  messages,
  loading,
  sidebarOpen,
  onNewConversation,
  onToggleSidebar,
  onSelectConversation,
  onDeleteConversation,
  onRenameConversation,
  onSubmitPrompt
}) => {
  const { mode } = useMode();
  const { t } = useLanguage();
  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-slate-50 to-slate-100 w-full">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxwYXR0ZXJuIGlkPSJwYXR0ZXJuIiB4PSIwIiB5PSIwIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiIHBhdHRlcm5UcmFuc2Zvcm09InJvdGF0ZSgzMCkiPjxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSIyIiBoZWlnaHQ9IjIiIGZpbGw9IiM2NDc0OEIiIGZpbGwtb3BhY2l0eT0iMC4wMyIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3QgeD0iMCIgeT0iMCIgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNwYXR0ZXJuKSIvPjwvc3ZnPg==')] opacity-50" />
      
      <AppHeader 
        onNewConversation={onNewConversation} 
        onToggleSidebar={onToggleSidebar} 
        sidebarOpen={sidebarOpen} 
      />
      
      {/* Mode Switch component */}
      <div className="relative z-10 flex justify-center py-2">
        <ModeSwitch />
        {mode === 'discuss' && (
          <div className="text-sm text-slate-500 text-center absolute -bottom-4">
            {t('discussDescription')}
          </div>
        )}
      </div>
      
      <div className="flex flex-1 relative z-10">
        <ConversationHistorySidebar 
          conversations={conversations}
          activeConversationId={activeConversationId}
          isOpen={sidebarOpen}
          onSelectConversation={onSelectConversation}
          onDeleteConversation={onDeleteConversation}
          onRenameConversation={onRenameConversation}
        />
        
        <MainContent 
          messages={messages}
          loading={loading}
          sidebarOpen={sidebarOpen}
          onSubmit={onSubmitPrompt}
        />
      </div>
      <ScrollButton />
    </div>
  );
};

export default MainLayout;
