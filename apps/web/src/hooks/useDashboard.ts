import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { apiClient } from '../services/api';

const AUTO_SYNC_INTERVAL_HOURS = 6; // Auto-sync if last sync was more than 6 hours ago

export function useDashboard(selectedDate?: string) {
  const queryClient = useQueryClient();
  const autoSyncAttempted = useRef(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['dashboard', selectedDate],
    queryFn: () => apiClient.getDashboard(selectedDate),
    refetchInterval: 60000, // Refresh every minute
    staleTime: 5 * 60 * 1000, // Consider data stale after 5 minutes
    gcTime: 30 * 60 * 1000, // Keep in cache for 30 minutes
  });

  // Prefetch adjacent dates for instant navigation
  useEffect(() => {
    if (selectedDate) {
      const date = new Date(selectedDate);

      // Prefetch previous day
      const prevDate = new Date(date);
      prevDate.setDate(prevDate.getDate() - 1);
      const prevDateStr = prevDate.toISOString().split('T')[0];
      queryClient.prefetchQuery({
        queryKey: ['dashboard', prevDateStr],
        queryFn: () => apiClient.getDashboard(prevDateStr),
        staleTime: 5 * 60 * 1000,
      });

      // Prefetch next day (if not future)
      const nextDate = new Date(date);
      nextDate.setDate(nextDate.getDate() + 1);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (nextDate <= today) {
        const nextDateStr = nextDate.toISOString().split('T')[0];
        queryClient.prefetchQuery({
          queryKey: ['dashboard', nextDateStr],
          queryFn: () => apiClient.getDashboard(nextDateStr),
          staleTime: 5 * 60 * 1000,
        });
      }
    }
  }, [selectedDate, queryClient]);

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
