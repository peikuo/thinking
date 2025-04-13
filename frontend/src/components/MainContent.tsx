import React from 'react';
import ConversationThread from '@/components/ConversationThread';
import PromptInput from '@/components/PromptInput';
import WelcomeScreen from '@/components/WelcomeScreen';
import { ConversationMessage } from '@/types/models';

interface MainContentProps {
  messages: ConversationMessage[];
  loading: boolean;
  sidebarOpen: boolean;
  onSubmit: (prompt: string) => void;
}

const MainContent: React.FC<MainContentProps> = ({
  messages,
  loading,
  sidebarOpen,
  onSubmit
}) => {
  const hasMessages = messages.length > 0;
  
  return (
    <main className={`flex-1 py-6 relative z-10 transition-all duration-300 ${sidebarOpen ? 'md:ml-64 container' : 'container-fluid px-4 md:px-8'}`}>
      <div className={`mx-auto ${sidebarOpen ? 'max-w-2xl' : 'w-full max-w-6xl'}`}>
        {!hasMessages ? (
          <WelcomeScreen />
        ) : (
          <div className="mb-8">
            <ConversationThread messages={messages} />
          </div>
        )}
        
        <div className="sticky bottom-6 backdrop-blur-sm bg-white/80 p-4 rounded-xl border border-gray-200 shadow-sm transition-all duration-300 hover:shadow-md">
          <PromptInput onSubmit={onSubmit} loading={loading} />
        </div>
      </div>
    </main>
  );
};

export default MainContent;
