/**
 * Test utility for ChatGPT-like URL navigation
 * This file contains functions to test the URL navigation behavior
 */

// Function to log URL changes
export function setupUrlChangeLogger() {
  console.log('Setting up URL change logger');
  
  // Log initial URL
  console.log('Initial URL:', window.location.href);
  
  // Listen for URL changes
  const originalPushState = history.pushState;
  history.pushState = function() {
    console.log('URL changed to:', arguments[2]);
    return originalPushState.apply(this, arguments as any);
  };
  
  // Listen for popstate events (back/forward navigation)
  window.addEventListener('popstate', () => {
    console.log('URL changed (popstate):', window.location.href);
  });
  
  return {
    // Test function to create a new conversation and check URL changes
    testNewConversation: async (submitPromptFn: (prompt: string) => Promise<void>) => {
      console.log('===== Testing New Conversation =====');
      console.log('Current URL before test:', window.location.href);
      
      // Submit a test prompt
      const testPrompt = 'This is a test prompt for URL navigation ' + Date.now();
      console.log('Submitting test prompt:', testPrompt);
      
      try {
        await submitPromptFn(testPrompt);
        console.log('Prompt submitted successfully');
        
        // Check if URL changed to include conversation ID
        setTimeout(() => {
          const currentUrl = window.location.href;
          console.log('URL after prompt submission:', currentUrl);
          
          if (currentUrl.includes('/c/')) {
            console.log('✅ SUCCESS: URL changed to include conversation ID');
          } else {
            console.log('❌ FAILURE: URL did not change to include conversation ID');
          }
        }, 1000); // Wait a bit for URL to update
      } catch (error) {
        console.error('Error submitting prompt:', error);
      }
    }
  };
}
