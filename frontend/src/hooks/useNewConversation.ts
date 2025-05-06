import { useCallback } from 'react';
import { useMode } from '@/contexts/ModeContext';
import { useDiscussMode } from './useDiscussMode';
import { useApp } from '@/contexts/AppContext';

/**
 * Custom hook to handle creating a new conversation, 
 * ensuring proper state reset in both chat and discuss modes
 */
export function useNewConversation() {
  const { mode } = useMode();
  const { resetDiscussion } = useDiscussMode();
  const { createNewConversation } = useApp();

  const handleNewConversation = useCallback(() => {
    // If in discuss mode, reset the discuss state
    if (mode === 'discuss') {
      // First create a new conversation in the history with a proper title
      const newId = createNewConversation();
      
      // Then reset the discussion state
      resetDiscussion();
      
      // Also directly clear localStorage to ensure complete reset
      localStorage.removeItem('thinking-discuss-responses');
      localStorage.removeItem('thinking-discuss-prompt');
      
      // Force a page reload to ensure all state is reset
      window.location.reload();
      return;
    }
    
    // Create a new conversation in chat mode
    createNewConversation();
  }, [mode, resetDiscussion, createNewConversation]);

  return handleNewConversation;
}
