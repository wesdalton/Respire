import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { apiClient } from '../services/api';

const AUTO_SYNC_INTERVAL_HOURS = 6; // Auto-sync if last sync was more than 6 hours ago

export function useDashboard() {
  const queryClient = useQueryClient();
  const autoSyncAttempted = useRef(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => apiClient.getDashboard(),
    refetchInterval: 60000, // Refresh every minute
    staleTime: 30000, // Consider data stale after 30 seconds
  });

  const syncMutation = useMutation({
    mutationFn: () => apiClient.syncWHOOP(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['health'] });
    },
    onError: (error) => {
      console.error('Auto-sync failed:', error);
      // Silently fail - user can manually sync if needed
    },
  });

  // Auto-sync effect
  useEffect(() => {
    // Only attempt auto-sync once per dashboard mount
    if (autoSyncAttempted.current || !data || isLoading || syncMutation.isPending) {
      return;
    }

    const lastSync = data.metrics?.last_sync;

    // If no last sync time, don't auto-sync (user needs to manually sync first)
    if (!lastSync) {
      return;
    }

    // Calculate hours since last sync
    const lastSyncDate = new Date(lastSync);
    const now = new Date();
    const hoursSinceSync = (now.getTime() - lastSyncDate.getTime()) / (1000 * 60 * 60);

    // Auto-sync if it's been more than the interval
    if (hoursSinceSync >= AUTO_SYNC_INTERVAL_HOURS) {
      console.log(`Auto-syncing WHOOP data (last sync: ${hoursSinceSync.toFixed(1)} hours ago)`);
      autoSyncAttempted.current = true;
      syncMutation.mutate();
    }
  }, [data, isLoading, syncMutation]);

  return {
    dashboard: data,
    isLoading,
    error,
    refetch,
    sync: syncMutation.mutate,
    isSyncing: syncMutation.isPending,
  };
}
