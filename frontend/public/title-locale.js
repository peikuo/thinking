// Dynamically set the page title based on user's language preference
(function() {
  function updateTitle() {
    // Check localStorage for language preference
    const lang = localStorage.getItem('ai-comparison-language') || 
                (navigator.language.startsWith('zh') ? 'zh' : 'en');
    
    // Set title based on language
    document.title = lang === 'zh' ? '集思广益' : 'Think Together';
  }
  
  // Update title immediately
  updateTitle();
  
  // Listen for storage changes (in case language is changed while page is open)
  window.addEventListener('storage', function(e) {
    if (e.key === 'ai-comparison-language') {
      updateTitle();
    }
  });
})();
