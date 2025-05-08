import React, { createContext, useContext, useState, useEffect } from 'react';

type Mode = 'chat' | 'discuss';

interface ModeContextType {
  mode: Mode;
  setMode: (mode: Mode) => void;
}

// Storage key for saving mode
const MODE_STORAGE_KEY = 'thinking-mode';

const ModeContext = createContext<ModeContextType | undefined>(undefined);

export const ModeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Initialize mode from localStorage or default to 'chat'
  const [mode, setModeState] = useState<Mode>(() => {
    try {
      const savedMode = localStorage.getItem(MODE_STORAGE_KEY);
      return (savedMode === 'discuss' ? 'discuss' : 'chat') as Mode;
    } catch (error) {
      console.error('Error loading mode from localStorage:', error);
      return 'chat';
    }
  });

  // Listen for mode change events from conversation selection
  useEffect(() => {
    const handleModeChange = (event: CustomEvent) => {
      const { newMode } = event.detail;
      if (newMode && (newMode === 'chat' || newMode === 'discuss')) {
        setModeState(newMode as Mode);
      }
    };

    // Add event listener for custom mode change event
    window.addEventListener('thinking-mode-changed', handleModeChange as EventListener);
    
    // Clean up event listener on unmount
    return () => {
      window.removeEventListener('thinking-mode-changed', handleModeChange as EventListener);
    };
  }, []);

  // Custom setMode function that updates both state and localStorage
  const setMode = (newMode: Mode) => {
    setModeState(newMode);
    try {
      localStorage.setItem(MODE_STORAGE_KEY, newMode);
    } catch (error) {
      console.error('Error saving mode to localStorage:', error);
    }
  };

  return (
    <ModeContext.Provider value={{ mode, setMode }}>
      {children}
    </ModeContext.Provider>
  );
};

export const useMode = () => {
  const context = useContext(ModeContext);
  if (context === undefined) {
    throw new Error('useMode must be used within a ModeProvider');
  }
  return context;
};
