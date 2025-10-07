import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';

export function useDashboard() {
  const queryClient = useQueryClient();

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
  });

  return {
    dashboard: data,
    isLoading,
    error,
    refetch,
    sync: syncMutation.mutate,
    isSyncing: syncMutation.isPending,
  };
}
