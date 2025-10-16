import { useState, useMemo } from 'react';
import { useHealth } from '../hooks/useHealth';
import HealthChart from '../components/dashboard/HealthChart';
import { Download, Calendar } from 'lucide-react';
import { format, subDays } from 'date-fns';

type DateRange = 7 | 14 | 30;

export default function History() {
  const [dateRange, setDateRange] = useState<DateRange>(30);

  const endDate = useMemo(() => new Date().toISOString().split('T')[0], []);
  const startDate = useMemo(() => {
    return subDays(new Date(), dateRange).toISOString().split('T')[0];
  }, [dateRange]);

  const { metrics, burnoutHistory, isLoading, error } = useHealth(startDate, endDate);

  const handleExportData = () => {
    // Placeholder for export functionality
    alert('Export functionality coming soon!');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-12 bg-gray-200 rounded w-1/3"></div>
            <div className="h-96 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading History</h2>
            <p className="text-red-600">
              {error instanceof Error ? error.message : 'Failed to load historical data'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Health History</h1>
            <p className="text-gray-600">View your health metrics and burnout trends over time</p>
          </div>

          <button
            onClick={handleExportData}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 shadow-md hover:shadow-lg"
          >
            <Download size={18} />
            Export Data
          </button>
        </div>

        {/* Date Range Selector */}
        <div className="bg-white rounded-lg shadow-md p-5">
          <div className="flex items-center gap-3 mb-4">
            <Calendar className="w-5 h-5 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-900">Date Range</h2>
          </div>

          <div className="flex flex-wrap gap-3">
            {[7, 14, 30].map((days) => (
              <button
                key={days}
                onClick={() => setDateRange(days as DateRange)}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                  dateRange === days
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Last {days} days
              </button>
            ))}
          </div>

          <div className="mt-3 text-sm text-gray-600">
            Showing data from {format(new Date(startDate), 'MMM d, yyyy')} to {format(new Date(endDate), 'MMM d, yyyy')}
          </div>
        </div>

        {/* Health Metrics Chart */}
        {metrics && metrics.length > 0 ? (
          <HealthChart
            data={metrics}
            metrics={['recovery_score', 'hrv', 'sleep_quality_score', 'day_strain']}
            maxDays={999} // Show all data, no limit - let date range buttons control it
          />
        ) : (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">No Health Data Available</h3>
            <p className="text-gray-600">Connect your WHOOP device or wait for data to sync.</p>
          </div>
        )}

        {/* Burnout History Table */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Burnout Risk History</h2>

          {burnoutHistory && burnoutHistory.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Date</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Risk Score</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Risk Level</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Confidence</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Data Points</th>
                  </tr>
                </thead>
                <tbody>
                  {burnoutHistory.map((entry) => {
                    const riskLevel = entry.risk_level ||
                      (entry.overall_risk_score >= 70 ? 'High' :
                       entry.overall_risk_score >= 40 ? 'Moderate' : 'Low');

                    const riskColor =
                      riskLevel === 'High' ? 'text-red-600 bg-red-50' :
                      riskLevel === 'Moderate' ? 'text-yellow-600 bg-yellow-50' :
                      'text-green-600 bg-green-50';

                    return (
                      <tr key={entry.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                        <td className="py-3 px-4 text-sm text-gray-800">
                          {format(new Date(entry.date), 'MMM d, yyyy')}
                        </td>
                        <td className="py-3 px-4">
                          <span className="text-sm font-semibold text-gray-900">
                            {entry.overall_risk_score.toFixed(1)}%
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${riskColor}`}>
                            {riskLevel}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-700">
                          {entry.confidence_score ? `${entry.confidence_score.toFixed(1)}%` : 'N/A'}
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-700">
                          {entry.data_points_used || 'N/A'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-5xl mb-3">📈</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">No Burnout History</h3>
              <p className="text-gray-600">Burnout risk calculations will appear here once you have enough data.</p>
            </div>
          )}
        </div>

        {/* Summary Stats */}
        {metrics && metrics.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow-md p-5">
              <div className="text-sm font-medium text-gray-600 mb-1">Avg Recovery</div>
              <div className="text-2xl font-bold text-blue-600">
                {(metrics.reduce((acc, m) => acc + (m.recovery_score || 0), 0) / metrics.length).toFixed(0)}%
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-5">
              <div className="text-sm font-medium text-gray-600 mb-1">Avg HRV</div>
              <div className="text-2xl font-bold text-green-600">
                {(metrics.reduce((acc, m) => acc + (m.hrv || 0), 0) / metrics.length).toFixed(0)} ms
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-5">
              <div className="text-sm font-medium text-gray-600 mb-1">Avg Sleep Quality</div>
              <div className="text-2xl font-bold text-purple-600">
                {(metrics.reduce((acc, m) => acc + (m.sleep_quality_score || 0), 0) / metrics.length).toFixed(0)}%
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-5">
              <div className="text-sm font-medium text-gray-600 mb-1">Avg Strain</div>
              <div className="text-2xl font-bold text-orange-600">
                {(metrics.reduce((acc, m) => acc + (m.day_strain || 0), 0) / metrics.length).toFixed(1)}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
