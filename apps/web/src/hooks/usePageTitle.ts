import { useEffect } from 'react';

/**
 * Custom hook to set the page title
 * @param title - The page title (will be suffixed with "- Respire")
 * @param dependencies - Optional dependencies array to update title when they change
 */
export function usePageTitle(title: string, dependencies: any[] = []) {
  useEffect(() => {
    const previousTitle = document.title;
    document.title = title ? `${title} - Respire` : 'Respire - AI-Powered Burnout Prevention & Health Tracking';

    // Cleanup: restore previous title on unmount
    return () => {
      document.title = previousTitle;
    };
  }, [title, ...dependencies]);
}
