import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useInView } from 'framer-motion';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Activity, Heart, Brain, Moon, AlertTriangle, TrendingUp, TrendingDown, Zap, Users, MessageSquare } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

// Real Respire app data structure - WHOOP metrics + mood + burnout prediction
const mockUsers = {
  alex: {
    name: 'Alex Chen',
    role: 'Senior Developer',
    currentBurnoutRisk: 78,
    weekData: [
      { date: 'Mon', recovery_score: 65, hrv: 45, strain: 12.4, sleep_quality: 72, mood_rating: 6, burnout_risk: 45 },
      { date: 'Tue', recovery_score: 58, hrv: 42, strain: 15.2, sleep_quality: 68, mood_rating: 5, burnout_risk: 58 },
      { date: 'Wed', recovery_score: 52, hrv: 38, strain: 16.8, sleep_quality: 61, mood_rating: 4, burnout_risk: 67 },
      { date: 'Thu', recovery_score: 41, hrv: 35, strain: 18.1, sleep_quality: 55, mood_rating: 3, burnout_risk: 78 },
      { date: 'Fri', recovery_score: 38, hrv: 32, strain: 19.2, sleep_quality: 48, mood_rating: 3, burnout_risk: 84 },
      { date: 'Sat', recovery_score: 45, hrv: 36, strain: 14.5, sleep_quality: 58, mood_rating: 4, burnout_risk: 82 },
      { date: 'Sun', recovery_score: 51, hrv: 39, strain: 12.1, sleep_quality: 64, mood_rating: 5, burnout_risk: 75 }
    ],
    aiInsights: [
      "Your HRV has declined 28% this week - a strong predictor of upcoming burnout",
      "High strain combined with poor recovery indicates overreaching",
      "Mood ratings correlate with declining sleep quality - classic burnout pattern"
    ]
  },
  sarah: {
    name: 'Sarah Miller',
    role: 'Product Manager',
    currentBurnoutRisk: 45,
    weekData: [
      { date: 'Mon', recovery_score: 78, hrv: 52, strain: 10.2, sleep_quality: 82, mood_rating: 7, burnout_risk: 28 },
      { date: 'Tue', recovery_score: 72, hrv: 49, strain: 12.1, sleep_quality: 79, mood_rating: 6, burnout_risk: 35 },
      { date: 'Wed', recovery_score: 69, hrv: 47, strain: 13.5, sleep_quality: 76, mood_rating: 6, burnout_risk: 42 },
      { date: 'Thu', recovery_score: 65, hrv: 45, strain: 14.8, sleep_quality: 71, mood_rating: 5, burnout_risk: 48 },
      { date: 'Fri', recovery_score: 61, hrv: 43, strain: 15.2, sleep_quality: 68, mood_rating: 5, burnout_risk: 52 },
      { date: 'Sat', recovery_score: 68, hrv: 46, strain: 11.8, sleep_quality: 74, mood_rating: 6, burnout_risk: 45 },
      { date: 'Sun', recovery_score: 73, hrv: 48, strain: 9.5, sleep_quality: 78, mood_rating: 7, burnout_risk: 38 }
    ],
    aiInsights: [
      "Gradual decline in recovery mid-week suggests building fatigue",
      "Weekend recovery pattern shows good stress management",
      "Maintain current workload to prevent escalation"
    ]
  },
  mike: {
    name: 'Mike Johnson',
    role: 'Design Lead',
    currentBurnoutRisk: 23,
    weekData: [
      { date: 'Mon', recovery_score: 85, hrv: 58, strain: 8.5, sleep_quality: 88, mood_rating: 8, burnout_risk: 18 },
      { date: 'Tue', recovery_score: 82, hrv: 56, strain: 9.2, sleep_quality: 86, mood_rating: 8, burnout_risk: 22 },
      { date: 'Wed', recovery_score: 79, hrv: 54, strain: 10.1, sleep_quality: 83, mood_rating: 7, burnout_risk: 26 },
      { date: 'Thu', recovery_score: 81, hrv: 55, strain: 9.8, sleep_quality: 85, mood_rating: 7, burnout_risk: 24 },
      { date: 'Fri', recovery_score: 84, hrv: 57, strain: 8.9, sleep_quality: 87, mood_rating: 8, burnout_risk: 21 },
      { date: 'Sat', recovery_score: 87, hrv: 59, strain: 7.2, sleep_quality: 90, mood_rating: 9, burnout_risk: 16 },
      { date: 'Sun', recovery_score: 89, hrv: 61, strain: 6.8, sleep_quality: 92, mood_rating: 9, burnout_risk: 14 }
    ],
    aiInsights: [
      "Excellent balance between strain and recovery",
      "Consistent sleep quality supporting optimal performance",
      "Low burnout risk - current patterns are sustainable"
    ]
  }
};

export const EnhancedDashboardDemo: React.FC = () => {
  const [selectedUser, setSelectedUser] = useState<'alex' | 'sarah' | 'mike'>('alex');
  const [selectedMetric, setSelectedMetric] = useState<'recovery_score' | 'hrv' | 'strain' | 'sleep_quality' | 'mood_rating' | 'burnout_risk'>('burnout_risk');

  const ref = useRef(null);
  const isInView = useInView(ref, { once: false, amount: 0.3 });

  const currentUser = mockUsers[selectedUser];

  // Chart data for selected metric
  const chartData = {
    labels: currentUser.weekData.map(d => d.date),
    datasets: [
      {
        label: selectedMetric.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        data: currentUser.weekData.map(d => d[selectedMetric]),
        borderColor: selectedMetric === 'burnout_risk' ? '#EF4444' :
                    selectedMetric === 'recovery_score' ? '#10B981' :
                    selectedMetric === 'hrv' ? '#3B82F6' :
                    selectedMetric === 'strain' ? '#F59E0B' :
                    selectedMetric === 'sleep_quality' ? '#8B5CF6' : '#EC4899',
        backgroundColor: selectedMetric === 'burnout_risk' ? 'rgba(239, 68, 68, 0.1)' :
                        selectedMetric === 'recovery_score' ? 'rgba(16, 185, 129, 0.1)' :
                        selectedMetric === 'hrv' ? 'rgba(59, 130, 246, 0.1)' :
                        selectedMetric === 'strain' ? 'rgba(245, 158, 11, 0.1)' :
                        selectedMetric === 'sleep_quality' ? 'rgba(139, 92, 246, 0.1)' : 'rgba(236, 72, 153, 0.1)',
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
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: selectedMetric === 'burnout_risk' ? 'rgba(239, 68, 68, 0.5)' : 'rgba(59, 130, 246, 0.5)',
        borderWidth: 2,
        cornerRadius: 12,
        padding: 16
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(0, 0, 0, 0.1)' },
        ticks: { color: '#6B7280', font: { size: 12 } }
      },
      y: {
        grid: { color: 'rgba(0, 0, 0, 0.1)' },
        ticks: { color: '#6B7280', font: { size: 12 } },
        beginAtZero: selectedMetric === 'mood_rating' ? false : true,
        max: selectedMetric === 'burnout_risk' ? 100 :
             selectedMetric === 'recovery_score' ? 100 :
             selectedMetric === 'sleep_quality' ? 100 :
             selectedMetric === 'hrv' ? 80 :
             selectedMetric === 'strain' ? 21 : 10
      }
    },
    animation: {
      duration: 1000,
      easing: 'easeInOutQuart' as const
    }
  };

  // Get risk level styling
  const getRiskStyling = (risk: number) => {
    if (risk >= 70) return { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-800', badge: 'bg-red-100 text-red-800', status: 'HIGH RISK' };
    if (risk >= 40) return { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-800', badge: 'bg-yellow-100 text-yellow-800', status: 'MODERATE' };
    return { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-800', badge: 'bg-green-100 text-green-800', status: 'LOW RISK' };
  };

  const riskStyling = getRiskStyling(currentUser.currentBurnoutRisk);

  const metrics = [
    { key: 'burnout_risk' as const, name: 'Burnout Risk', icon: AlertTriangle, color: 'text-red-500', unit: '%' },
    { key: 'recovery_score' as const, name: 'Recovery', icon: Heart, color: 'text-green-500', unit: '%' },
    { key: 'hrv' as const, name: 'HRV', icon: Activity, color: 'text-blue-500', unit: 'ms' },
    { key: 'strain' as const, name: 'Strain', icon: Zap, color: 'text-yellow-500', unit: '' },
    { key: 'sleep_quality' as const, name: 'Sleep', icon: Moon, color: 'text-purple-500', unit: '%' },
    { key: 'mood_rating' as const, name: 'Mood', icon: Brain, color: 'text-pink-500', unit: '/10' },
  ];

  // Get latest values for today's snapshot
  const latestData = currentUser.weekData[currentUser.weekData.length - 1];

  return (
    <div ref={ref} className="w-full space-y-6">
      {/* User Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${
              currentUser.currentBurnoutRisk >= 70 ? 'from-red-500 to-red-600' :
              currentUser.currentBurnoutRisk >= 40 ? 'from-yellow-500 to-yellow-600' :
              'from-green-500 to-green-600'
            } flex items-center justify-center shadow-lg`}>
              <Users className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900">{currentUser.name}</h3>
              <p className="text-sm text-gray-600">{currentUser.role}</p>
            </div>
          </div>
          <Badge className={riskStyling.badge}>
            {riskStyling.status}
          </Badge>
        </div>

        {/* User Selector */}
        <div className="flex space-x-2">
          {Object.entries(mockUsers).map(([key, user]) => (
            <button
              key={key}
              onClick={() => setSelectedUser(key as any)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedUser === key
                  ? 'bg-primary-100 text-primary-700 border border-primary-200'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {user.name.split(' ')[0]}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart */}
        <Card className="lg:col-span-2 p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-gray-900">7-Day Trend Analysis</h4>
          </div>

          {/* Metric Selector */}
          <div className="flex flex-wrap gap-2 mb-4">
            {metrics.map(({ key, name, icon: Icon, color, unit }) => (
              <button
                key={key}
                onClick={() => setSelectedMetric(key)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  selectedMetric === key
                    ? 'bg-primary-100 text-primary-700 border border-primary-200'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Icon className={`w-4 h-4 ${selectedMetric === key ? color : 'text-gray-400'}`} />
                <span>{name}</span>
              </button>
            ))}
          </div>

          <div className="h-64">
            <Line data={chartData} options={chartOptions} />
          </div>
        </Card>

        {/* Burnout Risk Summary */}
        <Card className={`p-6 ${riskStyling.bg} ${riskStyling.border}`}>
          <div className="text-center mb-6">
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-r from-red-500 to-red-600 flex items-center justify-center">
              <span className="text-2xl font-bold text-white">{currentUser.currentBurnoutRisk}%</span>
            </div>
            <h4 className={`text-lg font-semibold mb-2 ${riskStyling.text}`}>
              {riskStyling.status}
            </h4>
            <p className="text-sm text-gray-600 mb-4">
              Based on ML analysis of biometric patterns
            </p>
          </div>

          {/* Today's Key Metrics */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Recovery</span>
              <span className="font-semibold">{latestData.recovery_score}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">HRV</span>
              <span className="font-semibold">{latestData.hrv}ms</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Strain</span>
              <span className="font-semibold">{latestData.strain}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Sleep</span>
              <span className="font-semibold">{latestData.sleep_quality}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Mood</span>
              <span className="font-semibold">{latestData.mood_rating}/10</span>
            </div>
          </div>

          <Button variant="primary" size="sm" className="w-full mt-4">
            View AI Recommendations
          </Button>
        </Card>
      </div>

      {/* AI Insights Section */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
            <MessageSquare className="w-5 h-5 text-white" />
          </div>
          <div>
            <h4 className="text-lg font-semibold text-gray-900">AI Pattern Analysis</h4>
            <p className="text-sm text-gray-600">Insights from biometric data fusion</p>
          </div>
        </div>

        <div className="space-y-3">
          {currentUser.aiInsights.map((insight, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
            >
              <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <Brain className="w-3 h-3 text-primary-600" />
              </div>
              <p className="text-gray-800 text-sm">{insight}</p>
            </motion.div>
          ))}
        </div>
      </Card>
    </div>
  );
};