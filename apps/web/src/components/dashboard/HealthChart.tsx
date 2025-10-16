import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import type { HealthMetric } from '../../types/index';

interface HealthChartProps {
  data: HealthMetric[];
  metrics: string[];
  maxDays?: number; // Optional override for max days to display
}

const metricConfig = {
  recovery_score: {
    color: '#3b82f6',
    label: 'Recovery',
  },
  hrv: {
    color: '#10b981',
    label: 'HRV',
  },
  sleep_quality_score: {
    color: '#8b5cf6',
    label: 'Sleep',
  },
  day_strain: {
    color: '#f59e0b',
    label: 'Strain',
  },
};

const HealthChart = ({ data, metrics, maxDays }: HealthChartProps) => {
  const [windowWidth, setWindowWidth] = useState(
    typeof window !== 'undefined' ? window.innerWidth : 1920
  );

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // If maxDays not provided, use responsive logic for dashboard
  const responsiveMaxDays = maxDays !== undefined ? maxDays :
    (windowWidth >= 1500 ? 14 : 7);

  const displayData = maxDays !== undefined ? data : data.slice(-responsiveMaxDays);

  // Transform data for recharts (data already ordered oldest to newest)
  const chartData = displayData.map((item) => ({
    date: format(new Date(item.date), 'MM/dd'),
    recovery_score: item.recovery_score,
    hrv: item.hrv,
    sleep_quality_score: item.sleep_quality_score,
    day_strain: item.day_strain,
  }));

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        Health Metrics Trend {displayData.length < data.length && `(Last ${displayData.length} days)`}
      </h3>

      <ResponsiveContainer width="100%" height={350}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickLine={{ stroke: '#e5e7eb' }}
          />
          <YAxis
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickLine={{ stroke: '#e5e7eb' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
            labelStyle={{ color: '#111827', fontWeight: 600 }}
          />
          <Legend
            wrapperStyle={{
              paddingTop: '20px',
            }}
            iconType="line"
          />
          {metrics.map((metric) => {
            const config = metricConfig[metric as keyof typeof metricConfig];
            return config ? (
              <Line
                key={metric}
                type="monotone"
                dataKey={metric}
                stroke={config.color}
                strokeWidth={2}
                name={config.label}
                dot={{ fill: config.color, r: 4 }}
                activeDot={{ r: 6 }}
              />
            ) : null;
          })}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default HealthChart;
