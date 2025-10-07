import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';

export function useHealth(startDate?: string, endDate?: string) {
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useQuery({
    queryKey: ['health-metrics', startDate, endDate],
    queryFn: () => apiClient.getHealthMetrics(startDate, endDate),
    enabled: !!startDate, // Only fetch if date range provided
  });

  const { data: burnoutHistory, isLoading: burnoutLoading } = useQuery({
    queryKey: ['burnout-history', startDate, endDate],
    queryFn: () => apiClient.getBurnoutHistory(startDate, endDate),
    enabled: !!startDate,
  });

  const { data: insights, isLoading: insightsLoading } = useQuery({
    queryKey: ['insights'],
    queryFn: () => apiClient.getInsights(),
  });

  return {
    metrics,
    burnoutHistory,
    insights,
    isLoading: metricsLoading || burnoutLoading || insightsLoading,
    error: metricsError,
  };
}
