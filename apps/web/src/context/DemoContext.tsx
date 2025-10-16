import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import DemoDataService from '../services/DemoDataService';

interface DemoContextType {
  isDemoMode: boolean;
  activateDemo: () => void;
  exitDemo: () => void;
  resetDemo: () => void;
  showUpgradePrompt: boolean;
  setShowUpgradePrompt: (show: boolean) => void;
}

const DemoContext = createContext<DemoContextType | undefined>(undefined);

export function DemoProvider({ children }: { children: ReactNode }) {
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [showUpgradePrompt, setShowUpgradePrompt] = useState(false);

  useEffect(() => {
    // Check if demo mode is active on mount
    const demoMode = localStorage.getItem('demo_mode');
    if (demoMode === 'active') {
      setIsDemoMode(true);

      // Initialize demo data if not already initialized
      if (!DemoDataService.isInitialized()) {
        DemoDataService.initialize();
      }
    }
  }, []);

  const activateDemo = () => {
    console.log('Activating demo mode...');
    localStorage.setItem('demo_mode', 'active');

    // Clear any existing auth tokens to avoid conflicts
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    DemoDataService.initialize();
    setIsDemoMode(true);
  };

  const exitDemo = () => {
    console.log('Exiting demo mode...');
    localStorage.setItem('demo_mode', 'exited');
    DemoDataService.clear();
    setIsDemoMode(false);

    // Redirect to login page
    window.location.href = '/login';
  };

  const resetDemo = () => {
    console.log('Resetting demo data...');
    DemoDataService.reset();
    // Reload the page to refresh with new data
    window.location.reload();
  };

  return (
    <DemoContext.Provider
      value={{
        isDemoMode,
        activateDemo,
        exitDemo,
        resetDemo,
        showUpgradePrompt,
        setShowUpgradePrompt,
      }}
    >
      {children}
    </DemoContext.Provider>
  );
}

export function useDemo() {
  const context = useContext(DemoContext);
  if (context === undefined) {
    throw new Error('useDemo must be used within a DemoProvider');
  }
  return context;
}
