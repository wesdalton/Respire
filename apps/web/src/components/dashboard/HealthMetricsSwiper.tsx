import { useState } from 'react';
import { ChevronLeft, ChevronRight, Activity, Heart, Moon, Zap } from 'lucide-react';
import { format } from 'date-fns';
import type { HealthMetric } from '../../types/index';

interface HealthMetricsSwiperProps {
  data: HealthMetric[];
}

interface MetricDisplayConfig {
  key: keyof Pick<HealthMetric, 'recovery_score' | 'hrv' | 'sleep_quality_score' | 'day_strain'>;
  label: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
  unit: string;
  max: number;
}

const METRICS: MetricDisplayConfig[] = [
  {
    key: 'recovery_score',
    label: 'Recovery',
    icon: <Activity className="w-5 h-5" />,
    color: 'rgb(59, 130, 246)',
    bgColor: 'bg-blue-50',
    unit: '%',
    max: 100,
  },
  {
    key: 'hrv',
    label: 'HRV',
    icon: <Heart className="w-5 h-5" />,
    color: 'rgb(16, 185, 129)',
    bgColor: 'bg-green-50',
    unit: 'ms',
    max: 100,
  },
  {
    key: 'sleep_quality_score',
    label: 'Sleep Quality',
    icon: <Moon className="w-5 h-5" />,
    color: 'rgb(139, 92, 246)',
    bgColor: 'bg-purple-50',
    unit: '%',
    max: 100,
  },
  {
    key: 'day_strain',
    label: 'Day Strain',
    icon: <Zap className="w-5 h-5" />,
    color: 'rgb(245, 158, 11)',
    bgColor: 'bg-orange-50',
    unit: '',
    max: 21,
  },
];

const CircularProgress = ({ value, max, color, size = 80, strokeWidth = 8 }: {
  value: number;
  max: number;
  color: string;
  size?: number;
  strokeWidth?: number;
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const percentage = Math.min((value / max) * 100, 100);
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <svg width={size} height={size} className="transform -rotate-90">
      {/* Background circle */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="#e5e7eb"
        strokeWidth={strokeWidth}
      />
      {/* Progress circle */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.5s ease' }}
      />
    </svg>
  );
};

const HealthMetricsSwiper = ({ data }: HealthMetricsSwiperProps) => {
  const [currentIndex, setCurrentIndex] = useState(data.length - 1); // Start with most recent
  const [touchStart, setTouchStart] = useState(0);
  const [touchEnd, setTouchEnd] = useState(0);

  const currentDay = data[currentIndex];
  const canGoPrev = currentIndex > 0;
  const canGoNext = currentIndex < data.length - 1;

  const handlePrev = () => {
    if (canGoPrev) setCurrentIndex(currentIndex - 1);
  };

  const handleNext = () => {
    if (canGoNext) setCurrentIndex(currentIndex + 1);
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchStart(e.targetTouches[0].clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd) return;

    const distance = touchStart - touchEnd;
    const minSwipeDistance = 50;

    if (distance > minSwipeDistance) {
      // Swiped left - go to next (newer)
      handleNext();
    } else if (distance < -minSwipeDistance) {
      // Swiped right - go to prev (older)
      handlePrev();
    }

    setTouchStart(0);
    setTouchEnd(0);
  };

  if (!currentDay) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 text-center">
        <p className="text-gray-500">No health data available</p>
      </div>
    );
  }

  const isToday = format(new Date(currentDay.date), 'yyyy-MM-dd') === format(new Date(), 'yyyy-MM-dd');

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header with navigation */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <button
            onClick={handlePrev}
            disabled={!canGoPrev}
            className={`p-2 rounded-lg transition-colors ${
              canGoPrev
                ? 'bg-white/80 hover:bg-white text-gray-700 shadow-sm'
                : 'bg-gray-100 text-gray-300 cursor-not-allowed'
            }`}
            aria-label="Previous day"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

          <div className="text-center">
            <h3 className="text-lg font-bold text-gray-900">
              {isToday ? 'Today' : format(new Date(currentDay.date), 'MMM d, yyyy')}
            </h3>
            <p className="text-xs text-gray-600 mt-0.5">
              {currentIndex + 1} of {data.length} days
            </p>
          </div>

          <button
            onClick={handleNext}
            disabled={!canGoNext}
            className={`p-2 rounded-lg transition-colors ${
              canGoNext
                ? 'bg-white/80 hover:bg-white text-gray-700 shadow-sm'
                : 'bg-gray-100 text-gray-300 cursor-not-allowed'
            }`}
            aria-label="Next day"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Swipeable content area */}
      <div
        className="p-6"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        <div className="grid grid-cols-2 gap-4">
          {METRICS.map((metric) => {
            const value = currentDay[metric.key] || 0;
            const displayValue = typeof value === 'number' ? value.toFixed(metric.key === 'hrv' || metric.key === 'day_strain' ? 1 : 0) : '0';

            return (
              <div
                key={metric.key}
                className={`${metric.bgColor} rounded-xl p-4 flex flex-col items-center justify-center touch-manipulation`}
              >
                {/* Icon */}
                <div
                  className="mb-3 p-2 rounded-lg bg-white/80 shadow-sm"
                  style={{ color: metric.color }}
                >
                  {metric.icon}
                </div>

                {/* Circular progress */}
                <div className="relative mb-3">
                  <CircularProgress
                    value={value}
                    max={metric.max}
                    color={metric.color}
                    size={90}
                    strokeWidth={8}
                  />
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-2xl font-bold text-gray-900">
                      {displayValue}
                    </span>
                    <span className="text-xs text-gray-600 font-medium">
                      {metric.unit}
                    </span>
                  </div>
                </div>

                {/* Label */}
                <p className="text-sm font-semibold text-gray-700 text-center">
                  {metric.label}
                </p>
              </div>
            );
          })}
        </div>

        {/* Swipe hint for first time */}
        {data.length > 1 && (
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-400">
              ← Swipe to view other days →
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default HealthMetricsSwiper;
