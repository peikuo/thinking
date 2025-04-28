import React, { useState } from 'react';
import ConversationThread from '@/components/ConversationThread';
import DiscussionThread from '@/components/DiscussionThread';
import PromptInput from '@/components/PromptInput';
import WelcomeScreen from '@/components/WelcomeScreen';
import { ConversationMessage } from '@/types/models';
import { useMode } from '@/contexts/ModeContext';
import { useDiscussMode } from '@/hooks/useDiscussMode';
import { useApp } from '@/contexts/AppContext';

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
  const { mode } = useMode();
  const { apiKeys } = useApp();
  const { 
    responses: discussResponses, 
    loading: discussLoading, 
    currentStep,
    streamingModel,
    lastPrompt,
    startDiscussion 
  } = useDiscussMode();
  
  const hasMessages = messages.length > 0;
  const isDiscussMode = mode === 'discuss';
  
  // State for discuss mode prompt, initialize with lastPrompt if available
  const [discussPrompt, setDiscussPrompt] = useState<string>(lastPrompt || "");
  
  // Handle discuss mode submit
  const handleDiscussSubmit = (prompt: string) => {
    setDiscussPrompt(prompt);
    startDiscussion(prompt, apiKeys);
  };
  
  // Choose the appropriate submit handler based on mode
  const handleSubmit = isDiscussMode ? handleDiscussSubmit : onSubmit;
  
  return (
    <main className={`flex-1 py-6 relative z-10 transition-all duration-300 ${sidebarOpen ? 'md:ml-64 container' : 'container-fluid px-4 md:px-8'}`}>
      <div className={`mx-auto ${sidebarOpen ? 'max-w-2xl' : 'w-full max-w-6xl'}`}>
        {!hasMessages && !discussPrompt && Object.keys(discussResponses).length === 0 ? (
          <WelcomeScreen />
        ) : (
          <div className="mb-8">
            {isDiscussMode ? (
              // Discussion Thread (sequential model responses)
              // Show the discussion thread if we have a prompt OR saved responses
              (discussPrompt || Object.keys(discussResponses).length > 0) && (
                <DiscussionThread 
                  userPrompt={discussPrompt || lastPrompt} // Use lastPrompt as fallback
                  responses={discussResponses}
                  loading={discussLoading}
                  currentStep={currentStep}
                  streamingModel={streamingModel}
                />
              )
            ) : (
              // Regular Conversation Thread
              <ConversationThread messages={messages} />
            )}
          </div>
        )}

        <div className="sticky bottom-0 py-4 bg-gradient-to-t from-slate-50 via-slate-50">
          <PromptInput 
            onSubmit={handleSubmit} 
            loading={isDiscussMode ? discussLoading : loading} 
          />
        </div>
      </div>
    </main>
  );
};

export default MainContent;
