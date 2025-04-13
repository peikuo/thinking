import React, { createContext, useContext, useState, useEffect } from 'react';

type LayoutType = 'default' | 'compact';

type LayoutContextType = {
  layout: LayoutType;
  setLayout: (layout: LayoutType) => void;
};

const LayoutContext = createContext<LayoutContextType | undefined>(undefined);

export const LayoutProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Get initial layout from localStorage or default to 'default'
  const getInitialLayout = (): LayoutType => {
    const savedLayout = localStorage.getItem('layout');
    return (savedLayout as LayoutType) || 'default';
  };

  const [layout, setLayout] = useState<LayoutType>(getInitialLayout);

  // Save layout to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('layout', layout);
  }, [layout]);

  return (
    <LayoutContext.Provider value={{ layout, setLayout }}>
      {children}
    </LayoutContext.Provider>
  );
};

// Custom hook to use the layout context
export const useLayout = () => {
  const context = useContext(LayoutContext);
  if (context === undefined) {
    throw new Error('useLayout must be used within a LayoutProvider');
  }
  return context;
};
