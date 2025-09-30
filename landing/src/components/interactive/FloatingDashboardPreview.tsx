import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Filler } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Activity, Heart, Brain, TrendingUp, AlertTriangle } from 'lucide-react';
import { mockBiometricData } from '../../data/mockData';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler);

export const FloatingDashboardPreview: React.FC = () => {
  const [currentDataIndex, setCurrentDataIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  // Cycle through data points to simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentDataIndex((prev) => (prev + 1) % mockBiometricData.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Floating animation trigger
  useEffect(() => {
    const toggleInterval = setInterval(() => {
      setIsVisible(prev => !prev);
    }, 10000);
    return () => clearInterval(toggleInterval);
  }, []);

  const currentData = mockBiometricData[currentDataIndex];
  const recentData = mockBiometricData.slice(Math.max(0, currentDataIndex - 3), currentDataIndex + 1);

  const chartData = {
    labels: recentData.map((_, i) => `Day ${i + 1}`),
    datasets: [
      {
        data: recentData.map(d => d.recovery_score),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { display: false },
      y: { display: false, min: 0, max: 100 }
    },
    animation: { duration: 1000 }
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 50 }}
          animate={{
            opacity: 1,
            scale: 1,
            y: 0,
            x: [0, 10, -10, 0],
            rotate: [0, 1, -1, 0]
          }}
          exit={{ opacity: 0, scale: 0.8, y: -50 }}
          transition={{
            duration: 0.8,
            x: { duration: 4, repeat: Infinity, ease: "easeInOut" },
            rotate: { duration: 4, repeat: Infinity, ease: "easeInOut" }
          }}
          className="absolute top-20 right-10 w-80 bg-white/90 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 p-4 z-10"
          style={{ transform: 'perspective(1000px) rotateX(5deg) rotateY(-5deg)' }}
        >
          {/* Mini Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-gray-700">Live Demo</span>
            </div>
            <div className="text-xs text-gray-500">
              {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>

          {/* Mini Metrics */}
          <div className="grid grid-cols-3 gap-2 mb-3">
            <motion.div
              key={`recovery-${currentDataIndex}`}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-2 text-center"
            >
              <Activity className="w-4 h-4 text-green-600 mx-auto mb-1" />
              <div className="text-lg font-bold text-green-700">
                {currentData.recovery_score}
              </div>
              <div className="text-xs text-green-600">Recovery</div>
            </motion.div>

            <motion.div
              key={`hrv-${currentDataIndex}`}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-2 text-center"
            >
              <Heart className="w-4 h-4 text-blue-600 mx-auto mb-1" />
              <div className="text-lg font-bold text-blue-700">
                {currentData.hrv}
              </div>
              <div className="text-xs text-blue-600">HRV ms</div>
            </motion.div>

            <motion.div
              key={`mood-${currentDataIndex}`}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-2 text-center"
            >
              <Brain className="w-4 h-4 text-purple-600 mx-auto mb-1" />
              <div className="text-lg font-bold text-purple-700">
                {currentData.mood_rating?.toFixed(1) || 'N/A'}
              </div>
              <div className="text-xs text-purple-600">Mood</div>
            </motion.div>
          </div>

          {/* Mini Chart */}
          <div className="h-16 mb-3">
            <Line data={chartData} options={chartOptions} />
          </div>

          {/* AI Insight */}
          <motion.div
            key={`insight-${currentDataIndex}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg p-2 border-l-2 border-amber-400"
          >
            <div className="flex items-start space-x-2">
              {currentData.recovery_score > 80 ? (
                <TrendingUp className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
              )}
              <div>
                <div className="text-xs font-medium text-gray-800">
                  {currentData.recovery_score > 80
                    ? 'Optimal Recovery'
                    : currentData.recovery_score > 60
                    ? 'Monitor Stress'
                    : 'Rest Recommended'}
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  {currentData.recovery_score > 80
                    ? 'Great work! Your recovery is on track.'
                    : 'Consider reducing strain today.'}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Floating Action */}
          <motion.button
            whileHover={{ scale: 1.02, boxShadow: '0 8px 25px rgba(0,0,0,0.15)' }}
            whileTap={{ scale: 0.98 }}
            onClick={() => {
              document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="w-full mt-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg py-2 text-sm font-medium hover:from-primary-700 hover:to-primary-800 transition-all duration-200"
          >
            Explore Full Demo →
          </motion.button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};