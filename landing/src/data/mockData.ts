import { BiometricData, BurnoutPrediction, Alert, Feature, Testimonial, PricingTier, Company } from '../types';

export const mockBiometricData: BiometricData[] = [
  { date: '2024-01-01', recovery_score: 85, hrv: 45, resting_hr: 52, strain: 12.5, sleep_quality: 88, mood_rating: 8 },
  { date: '2024-01-02', recovery_score: 72, hrv: 38, resting_hr: 55, strain: 15.2, sleep_quality: 76, mood_rating: 6 },
  { date: '2024-01-03', recovery_score: 68, hrv: 35, resting_hr: 58, strain: 16.8, sleep_quality: 71, mood_rating: 5 },
  { date: '2024-01-04', recovery_score: 79, hrv: 41, resting_hr: 54, strain: 13.9, sleep_quality: 82, mood_rating: 7 },
  { date: '2024-01-05', recovery_score: 91, hrv: 48, resting_hr: 50, strain: 10.2, sleep_quality: 92, mood_rating: 9 },
  { date: '2024-01-06', recovery_score: 87, hrv: 46, resting_hr: 51, strain: 11.8, sleep_quality: 89, mood_rating: 8 },
  { date: '2024-01-07', recovery_score: 75, hrv: 39, resting_hr: 56, strain: 14.6, sleep_quality: 78, mood_rating: 6 },
];

export const mockPrediction: BurnoutPrediction = {
  risk_score: 32,
  confidence: 0.87,
  trend: 'stable',
  factors: {
    recovery: 75,
    sleep: 82,
    hrv: 68,
    mood: 70,
    strain: 45
  }
};

export const mockAlerts: Alert[] = [
  {
    id: '1',
    type: 'warning',
    title: 'Elevated Strain Pattern',
    message: 'Your strain has been consistently high for 3 days. Consider a recovery day.',
    timestamp: '2024-01-07T08:30:00Z',
    dismissed: false
  },
  {
    id: '2',
    type: 'info',
    title: 'Sleep Quality Improving',
    message: 'Great job! Your sleep quality has improved 15% this week.',
    timestamp: '2024-01-06T22:15:00Z',
    dismissed: false
  },
  {
    id: '3',
    type: 'critical',
    title: 'Burnout Risk Elevated',
    message: 'Multiple indicators suggest increased burnout risk. Time for intervention.',
    timestamp: '2024-01-05T15:45:00Z',
    dismissed: true
  }
];

export const features: Feature[] = [
  {
    id: 'real-time',
    title: 'WHOOP API Integration',
    description: 'OAuth 2.0 flow to connect with WHOOP and fetch daily health metrics',
    icon: 'Activity',
    metrics: ['OAuth 2.0', 'Daily sync', '20+ metrics'],
    visual: 'dashboard-realtime.gif'
  },
  {
    id: 'ai-prediction',
    title: 'Burnout Risk Algorithm',
    description: 'Multi-factor scoring system analyzing recovery, mood, HRV, sleep, and strain patterns',
    icon: 'Brain',
    metrics: ['5 key factors', 'Weighted scoring', 'Trend analysis'],
    visual: 'ai-models.png'
  },
  {
    id: 'team-insights',
    title: 'Interactive Visualizations',
    description: 'Plotly charts and Apple-inspired UI for exploring health trends',
    icon: 'Users',
    metrics: ['Plotly charts', 'Correlation maps', 'Clean design'],
    visual: 'team-dashboard.png'
  },
  {
    id: 'integrations',
    title: 'AI-Powered Insights',
    description: 'OpenAI API integration provides personalized recommendations based on your data',
    icon: 'Zap',
    metrics: ['OpenAI GPT', 'Context-aware', 'Personalized'],
    visual: 'integrations.png'
  }
];

export const testimonials: Testimonial[] = [
  {
    id: '1',
    name: 'Early User',
    title: 'Software Engineer',
    company: 'Tech Industry',
    avatar: 'https://images.unsplash.com/photo-1494790108755-2616b2e1b1d3?w=150',
    quote: "As someone who also tracks WHOOP data, this project demonstrates a really thoughtful approach to analyzing health patterns. The visualizations make it easy to spot trends.",
    metrics: [
      { label: 'Project Status', value: 'Beta' },
      { label: 'Open Source', value: 'Yes' }
    ]
  },
  {
    id: '2',
    name: 'Beta Tester',
    title: 'Student Athlete',
    company: 'UPenn',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150',
    quote: "The correlation between my recovery scores and how I actually felt was eye-opening. This tool helps me understand when I need to dial back the intensity.",
    metrics: [
      { label: 'Personal Use', value: '3+ months' },
      { label: 'Data Points', value: '90+ days' }
    ]
  },
  {
    id: '3',
    name: 'Peer Reviewer',
    title: 'CS Student',
    company: 'UPenn',
    avatar: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=150',
    quote: "Impressive full-stack implementation with clean code architecture. The API integration and data pipeline show strong software engineering fundamentals.",
    metrics: [
      { label: 'Code Quality', value: 'High' },
      { label: 'Tech Stack', value: 'Modern' }
    ]
  }
];

export const pricingTiers: PricingTier[] = [
  {
    id: 'individual',
    name: 'Individual',
    price: 19,
    period: 'month',
    description: 'Perfect for professionals who want to optimize their personal performance',
    features: [
      'Personal dashboard',
      'Wearable device integration',
      'Basic AI insights',
      'Mobile app access',
      'Email support'
    ],
    cta: 'Start Free Trial'
  },
  {
    id: 'team',
    name: 'Team',
    price: 49,
    period: 'month',
    description: 'Ideal for teams and managers who want to prevent collective burnout',
    features: [
      'Everything in Individual',
      'Team analytics dashboard',
      'Manager insights',
      'Slack/Teams integration',
      'Advanced AI models',
      'Priority support'
    ],
    highlighted: true,
    cta: 'Start Free Trial'
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 0,
    period: 'month',
    description: 'Custom solution for organizations with advanced security and compliance needs',
    features: [
      'Everything in Team',
      'SSO/SAML integration',
      'Custom integrations',
      'Dedicated success manager',
      'SLA guarantees',
      'Custom reporting',
      'White-label options'
    ],
    cta: 'Contact Sales'
  }
];

export const trustedCompanies: Company[] = [
  { id: '1', name: 'WHOOP', logo: '/logos/whoop.svg', employees: 'Data Source', industry: 'Wearables' },
  { id: '2', name: 'Flask', logo: '/logos/flask.svg', employees: 'Backend', industry: 'Framework' },
  { id: '3', name: 'Supabase', logo: '/logos/supabase.svg', employees: 'Database', industry: 'Cloud' },
  { id: '4', name: 'Plotly', logo: '/logos/plotly.svg', employees: 'Visualization', industry: 'Data' },
  { id: '5', name: 'OpenAI', logo: '/logos/openai.svg', employees: 'AI Insights', industry: 'AI' },
  { id: '6', name: 'Python', logo: '/logos/python.svg', employees: 'Core Lang', industry: 'Language' },
];

export const stats = [
  { label: 'Lines of Code', value: '~2,000' },
  { label: 'WHOOP Metrics', value: '20+' },
  { label: 'Tech Stack', value: 'Modern' },
  { label: 'Project Type', value: 'Passion' },
];

export const integrations = [
  { name: 'WHOOP', logo: '/integrations/whoop.svg', category: 'Wearables' },
  { name: 'Oura Ring', logo: '/integrations/oura.svg', category: 'Wearables' },
  { name: 'Apple Watch', logo: '/integrations/apple-watch.svg', category: 'Wearables' },
  { name: 'Fitbit', logo: '/integrations/fitbit.svg', category: 'Wearables' },
  { name: 'Garmin', logo: '/integrations/garmin.svg', category: 'Wearables' },
  { name: 'Slack', logo: '/integrations/slack.svg', category: 'Communication' },
  { name: 'Microsoft Teams', logo: '/integrations/teams.svg', category: 'Communication' },
  { name: 'JIRA', logo: '/integrations/jira.svg', category: 'Productivity' },
  { name: 'Notion', logo: '/integrations/notion.svg', category: 'Productivity' },
  { name: 'Zapier', logo: '/integrations/zapier.svg', category: 'Automation' },
];