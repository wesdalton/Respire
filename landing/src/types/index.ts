export interface BiometricData {
  date: string;
  recovery_score: number;
  hrv: number;
  resting_hr: number;
  strain: number;
  sleep_quality: number;
  mood_rating?: number;
}

export interface BurnoutPrediction {
  risk_score: number;
  confidence: number;
  trend: 'improving' | 'stable' | 'declining';
  factors: {
    recovery: number;
    sleep: number;
    hrv: number;
    mood: number;
    strain: number;
  };
}

export interface Alert {
  id: string;
  type: 'warning' | 'critical' | 'info';
  title: string;
  message: string;
  timestamp: string;
  dismissed: boolean;
}

export interface Feature {
  id: string;
  title: string;
  description: string;
  icon: string;
  metrics?: string[];
  visual?: string;
}

export interface Testimonial {
  id: string;
  name: string;
  title: string;
  company: string;
  avatar: string;
  quote: string;
  metrics?: {
    label: string;
    value: string;
  }[];
}

export interface PricingTier {
  id: string;
  name: string;
  price: number;
  period: 'month' | 'year';
  description: string;
  features: string[];
  highlighted?: boolean;
  cta: string;
}

export interface Company {
  id: string;
  name: string;
  logo: string;
  employees?: string;
  industry?: string;
}

export interface DemoState {
  currentUser: string;
  timeRange: '7d' | '30d' | '90d';
  selectedMetrics: string[];
  realTimeEnabled: boolean;
}