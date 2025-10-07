import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';

export function useMood() {
  const queryClient = useQueryClient();

  const { data: moods, isLoading, error } = useQuery({
    queryKey: ['moods'],
    queryFn: () => apiClient.getMoodRatings(),
  });

  const { data: stats } = useQuery({
    queryKey: ['mood-stats'],
    queryFn: () => apiClient.getMoodStats(),
  });

  const createMutation = useMutation({
    mutationFn: (data: { date: string; rating: number; notes?: string }) =>
      apiClient.createMoodRating(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['moods'] });
      queryClient.invalidateQueries({ queryKey: ['mood-stats'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: { date: string; rating: number; notes?: string }) =>
      apiClient.updateMoodRating(data.date, data.rating, data.notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['moods'] });
      queryClient.invalidateQueries({ queryKey: ['mood-stats'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (date: string) => apiClient.deleteMoodRating(date),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['moods'] });
      queryClient.invalidateQueries({ queryKey: ['mood-stats'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  return {
    moods,
    stats,
    isLoading,
    error,
    createMood: createMutation.mutate,
    updateMood: updateMutation.mutate,
    deleteMood: deleteMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
