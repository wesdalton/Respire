import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Activity, Heart, Brain, Moon, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { mockBiometricData, mockPrediction, mockAlerts } from '../../data/mockData';
import { BiometricData } from '../../types';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

export const DashboardDemo: React.FC = () => {
  const [currentData, setCurrentData] = useState<BiometricData[]>(mockBiometricData);
  const [selectedMetric, setSelectedMetric] = useState<'recovery_score' | 'hrv' | 'strain' | 'mood_rating'>('recovery_score');
  const [isRealTime, setIsRealTime] = useState(false);

  // Simulate real-time data updates
  useEffect(() => {
    if (!isRealTime) return;

    const interval = setInterval(() => {
      setCurrentData(prev => {
        const newData = [...prev];
        const lastData = newData[newData.length - 1];
        const newPoint = {
          ...lastData,
          date: new Date(Date.now() + Math.random() * 1000000).toISOString().split('T')[0],
          recovery_score: Math.max(20, Math.min(100, lastData.recovery_score + (Math.random() - 0.5) * 20)),
          hrv: Math.max(20, Math.min(80, lastData.hrv + (Math.random() - 0.5) * 10)),
          strain: Math.max(5, Math.min(20, lastData.strain + (Math.random() - 0.5) * 3)),
          mood_rating: Math.max(1, Math.min(10, (lastData.mood_rating || 5) + (Math.random() - 0.5) * 2))
        };
        return [...newData.slice(-6), newPoint];
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [isRealTime]);

  const chartData = {
    labels: currentData.map(d => new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
    datasets: [
      {
        label: selectedMetric.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        data: currentData.map(d => d[selectedMetric]),
        borderColor: selectedMetric === 'recovery_score' ? '#10B981' :
                    selectedMetric === 'hrv' ? '#3B82F6' :
                    selectedMetric === 'strain' ? '#F59E0B' : '#8B5CF6',
        backgroundColor: selectedMetric === 'recovery_score' ? 'rgba(16, 185, 129, 0.1)' :
                        selectedMetric === 'hrv' ? 'rgba(59, 130, 246, 0.1)' :
                        selectedMetric === 'strain' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(139, 92, 246, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 6,
        pointHoverRadius: 8,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          color: '#6B7280'
        }
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          color: '#6B7280'
        },
        beginAtZero: selectedMetric !== 'mood_rating'
      }
    },
    animation: {
      duration: isRealTime ? 500 : 1000,
      easing: 'easeInOutQuart' as const
    }
  };

  const metrics = [
    { key: 'recovery_score', label: 'Recovery', icon: Activity, color: 'success', value: currentData[currentData.length - 1]?.recovery_score || 0 },
    { key: 'hrv', label: 'HRV', icon: Heart, color: 'primary', value: currentData[currentData.length - 1]?.hrv || 0 },
    { key: 'strain', label: 'Strain', icon: Brain, color: 'warning', value: currentData[currentData.length - 1]?.strain || 0 },
    { key: 'mood_rating', label: 'Mood', icon: Moon, color: 'neutral', value: currentData[currentData.length - 1]?.mood_rating || 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
      >
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Live Dashboard Demo</h3>
          <p className="text-gray-600">Interactive preview of real-time health monitoring</p>
        </div>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsRealTime(!isRealTime)}
          className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
            isRealTime
              ? 'bg-success-100 text-success-800 border border-success-200'
              : 'bg-gray-100 text-gray-800 border border-gray-200 hover:bg-gray-200'
          }`}
        >
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
            isRealTime ? 'bg-success-500 animate-pulse' : 'bg-gray-400'
          }`} />
          {isRealTime ? 'Live Updates On' : 'Enable Live Updates'}
        </motion.button>
      </motion.div>

      {/* Metrics Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          const isSelected = selectedMetric === metric.key;

          return (
            <motion.div
              key={metric.key}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 + index * 0.1 }}
              whileHover={{ scale: 1.02 }}
              onClick={() => setSelectedMetric(metric.key as any)}
              className={`cursor-pointer transition-all duration-200 ${
                isSelected ? 'ring-2 ring-primary-500' : ''
              }`}
            >
              <Card className={`text-center ${isSelected ? 'bg-primary-50 border-primary-200' : ''}`}>
                <Icon className={`w-8 h-8 mx-auto mb-2 ${
                  metric.color === 'success' ? 'text-success-500' :
                  metric.color === 'primary' ? 'text-primary-500' :
                  metric.color === 'warning' ? 'text-warning-500' : 'text-gray-500'
                }`} />
                <div className="text-2xl font-bold text-gray-900 mb-1">
                  {metric.value.toFixed(metric.key === 'mood_rating' ? 1 : 0)}
                  {metric.key === 'hrv' && 'ms'}
                  {metric.key === 'recovery_score' && '%'}
                  {metric.key === 'mood_rating' && '/10'}
                </div>
                <div className="text-sm text-gray-600">{metric.label}</div>
              </Card>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="p-6">
          <div className="h-64 mb-4">
            <Line data={chartData} options={chartOptions} />
          </div>
        </Card>
      </motion.div>

      {/* Burnout Risk Gauge */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 lg:grid-cols-3 gap-6"
      >
        {/* Risk Gauge */}
        <Card className="text-center p-8">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Burnout Risk</h4>
          <div className="relative w-32 h-32 mx-auto mb-4">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="rgba(229, 231, 235, 1)"
                strokeWidth="8"
                fill="none"
              />
              <motion.circle
                cx="64"
                cy="64"
                r="56"
                stroke={mockPrediction.risk_score < 30 ? '#10B981' :
                       mockPrediction.risk_score < 60 ? '#F59E0B' : '#EF4444'}
                strokeWidth="8"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 56}`}
                initial={{ strokeDashoffset: 2 * Math.PI * 56 }}
                animate={{
                  strokeDashoffset: 2 * Math.PI * 56 * (1 - mockPrediction.risk_score / 100)
                }}
                transition={{ duration: 2, ease: "easeOut" }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {mockPrediction.risk_score}%
                </div>
                <div className="text-xs text-gray-500">Risk Score</div>
              </div>
            </div>
          </div>
          <Badge variant={mockPrediction.risk_score < 30 ? 'success' :
                        mockPrediction.risk_score < 60 ? 'warning' : 'danger'}>
            {mockPrediction.risk_score < 30 ? 'Low Risk' :
             mockPrediction.risk_score < 60 ? 'Moderate Risk' : 'High Risk'}
          </Badge>
        </Card>

        {/* AI Insights */}
        <Card className="lg:col-span-2">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">AI Insights & Predictions</h4>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <TrendingUp className="w-5 h-5 text-success-500 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Recovery Trending Up</p>
                <p className="text-sm text-gray-600">Your recovery score has improved 15% this week</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-warning-500 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Strain Pattern Alert</p>
                <p className="text-sm text-gray-600">Consider a recovery day - strain elevated for 3+ days</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Brain className="w-5 h-5 text-primary-500 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">HRV Analysis</p>
                <p className="text-sm text-gray-600">Variability suggests good autonomic nervous system health</p>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Recent Alerts */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Recent Alerts</h4>
          <div className="space-y-3">
            <AnimatePresence>
              {mockAlerts.filter(alert => !alert.dismissed).map((alert, index) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-3 rounded-lg border-l-4 ${
                    alert.type === 'warning' ? 'bg-warning-50 border-warning-400' :
                    alert.type === 'critical' ? 'bg-danger-50 border-danger-400' :
                    'bg-primary-50 border-primary-400'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-gray-900 text-sm">{alert.title}</p>
                      <p className="text-gray-600 text-sm mt-1">{alert.message}</p>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </Card>
      </motion.div>
    </div>
  );
};