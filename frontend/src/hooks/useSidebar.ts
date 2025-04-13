import { useState, useEffect, useCallback } from 'react';

export function useSidebar() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Load sidebar state from localStorage on mount
  useEffect(() => {
    const savedSidebarState = localStorage.getItem('ai-comparison-sidebar-state');
    if (savedSidebarState) {
      setSidebarOpen(savedSidebarState === 'open');
    }
  }, []);

  // Save sidebar state to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('ai-comparison-sidebar-state', sidebarOpen ? 'open' : 'closed');
  }, [sidebarOpen]);

  const toggleSidebar = useCallback(() => {
    setSidebarOpen(prev => !prev);
  }, []);

  return {
    sidebarOpen,
    toggleSidebar
  };
}
