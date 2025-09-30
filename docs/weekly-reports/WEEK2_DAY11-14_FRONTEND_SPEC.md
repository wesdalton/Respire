# Week 2, Days 11-14: Frontend Development Specification

## Overview
Complete React/TypeScript frontend for the Respire burnout prevention platform, integrating with all 21 backend API endpoints.

## Technology Stack
- **Framework**: React 18 with TypeScript
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors
- **State Management**: React Query (@tanstack/react-query)
- **Charts**: Recharts
- **UI**: Tailwind CSS + lucide-react icons
- **Date Handling**: date-fns

## Architecture

### Directory Structure
```
apps/web/src/
├── components/          # Reusable UI components
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── SignupForm.tsx
│   ├── dashboard/
│   │   ├── MetricsCard.tsx
│   │   ├── BurnoutGauge.tsx
│   │   ├── HealthChart.tsx
│   │   ├── MoodCalendar.tsx
│   │   └── InsightCard.tsx
│   ├── mood/
│   │   ├── MoodEntry.tsx
│   │   └── MoodHistory.tsx
│   ├── whoop/
│   │   ├── ConnectionStatus.tsx
│   │   └── SyncButton.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Layout.tsx
├── pages/               # Page components
│   ├── Login.tsx
│   ├── Signup.tsx
│   ├── Dashboard.tsx
│   ├── Mood.tsx
│   ├── History.tsx
│   ├── Insights.tsx
│   └── Settings.tsx
├── context/             # React Context
│   └── AuthContext.tsx
├── services/            # API clients
│   └── api.ts
├── types/               # TypeScript types
│   └── index.ts
├── hooks/               # Custom hooks
│   ├── useAuth.ts
│   ├── useDashboard.ts
│   └── useMood.ts
├── utils/               # Helper functions
│   └── formatters.ts
├── App.tsx              # Main app with routing
└── main.tsx             # Entry point
```

## Core Components

### 1. Authentication Components

**LoginForm.tsx**
```tsx
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { signin } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await signin(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full px-4 py-2 border rounded-lg"
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full px-4 py-2 border rounded-lg"
      />
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
      >
        Sign In
      </button>
    </form>
  );
}
```

### 2. Dashboard Components

**MetricsCard.tsx** - Display latest health metrics
```tsx
interface MetricsCardProps {
  title: string;
  value?: number;
  unit?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'stable';
  color: 'blue' | 'green' | 'purple' | 'orange';
}

export function MetricsCard({ title, value, unit, icon, trend, color }: MetricsCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
        {trend && <TrendIndicator trend={trend} />}
      </div>
      <h3 className="text-gray-600 text-sm mb-1">{title}</h3>
      <div className="flex items-baseline gap-1">
        <span className="text-3xl font-bold text-gray-900">
          {value !== undefined ? value : '--'}
        </span>
        {unit && <span className="text-gray-500 text-sm">{unit}</span>}
      </div>
    </div>
  );
}
```

**BurnoutGauge.tsx** - Circular risk gauge
```tsx
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';

export function BurnoutGauge({ risk_score, risk_level }: { risk_score: number; risk_level: string }) {
  const getColor = (level: string) => {
    switch (level) {
      case 'low': return '#10b981';
      case 'moderate': return '#f59e0b';
      case 'high': return '#f97316';
      case 'critical': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div className="w-48 h-48 mx-auto">
      <CircularProgressbar
        value={risk_score}
        text={`${risk_score}%`}
        styles={buildStyles({
          pathColor: getColor(risk_level),
          textColor: getColor(risk_level),
          trailColor: '#e5e7eb',
        })}
      />
      <p className="text-center mt-4 font-semibold capitalize">{risk_level} Risk</p>
    </div>
  );
}
```

**HealthChart.tsx** - Line chart for metrics over time
```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

export function HealthChart({ data, metrics }: { data: HealthMetric[]; metrics: string[] }) {
  const chartData = data.map(m => ({
    date: format(new Date(m.date), 'MM/dd'),
    recovery: m.recovery_score,
    hrv: m.hrv,
    sleep: m.sleep_quality_score,
    strain: m.day_strain,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        {metrics.includes('recovery') && <Line type="monotone" dataKey="recovery" stroke="#3b82f6" />}
        {metrics.includes('hrv') && <Line type="monotone" dataKey="hrv" stroke="#10b981" />}
        {metrics.includes('sleep') && <Line type="monotone" dataKey="sleep" stroke="#8b5cf6" />}
        {metrics.includes('strain') && <Line type="monotone" dataKey="strain" stroke="#f59e0b" />}
      </LineChart>
    </ResponsiveContainer>
  );
}
```

### 3. Mood Tracking Components

**MoodEntry.tsx** - Quick mood rating input
```tsx
export function MoodEntry({ onSubmit }: { onSubmit: (rating: number, notes: string) => void }) {
  const [rating, setRating] = useState(5);
  const [notes, setNotes] = useState('');

  const emojis = ['😢', '😟', '😐', '🙂', '😊', '😃', '🤗', '😄', '🥳', '🤩'];

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">How are you feeling today?</h3>

      <div className="flex justify-between mb-6">
        {emojis.map((emoji, index) => (
          <button
            key={index}
            onClick={() => setRating(index + 1)}
            className={`text-3xl p-2 rounded-lg transition-all ${
              rating === index + 1 ? 'bg-blue-100 scale-110' : 'hover:bg-gray-100'
            }`}
          >
            {emoji}
          </button>
        ))}
      </div>

      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Optional notes..."
        className="w-full px-4 py-2 border rounded-lg mb-4"
        rows={3}
      />

      <button
        onClick={() => onSubmit(rating, notes)}
        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
      >
        Save Mood Rating
      </button>
    </div>
  );
}
```

### 4. Insight Components

**InsightCard.tsx** - Display AI insights
```tsx
export function InsightCard({ insight }: { insight: AIInsight }) {
  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl shadow-lg p-6">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="w-5 h-5 text-purple-600" />
        <span className="text-sm font-medium text-purple-600 uppercase">AI Insight</span>
      </div>

      <h3 className="text-xl font-bold text-gray-900 mb-3">{insight.title}</h3>

      <p className="text-gray-700 mb-4 whitespace-pre-line">{insight.content}</p>

      {insight.recommendations && insight.recommendations.items.length > 0 && (
        <div className="border-t pt-4">
          <h4 className="font-semibold text-gray-900 mb-2">Recommendations:</h4>
          <ul className="space-y-2">
            {insight.recommendations.items.map((rec, i) => (
              <li key={i} className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

## Pages

### Dashboard Page
**Features:**
- Summary metrics cards (recovery, HRV, mood, burnout risk)
- Burnout risk gauge with visual indicator
- Health metrics chart (last 7-14 days)
- Latest AI insight
- Quick mood entry
- WHOOP connection status
- Sync button

**API Calls:**
- GET `/api/health/dashboard` - Main data
- POST `/api/mood/` - Create mood rating
- POST `/api/whoop/sync/manual` - Manual sync

### Mood Tracking Page
**Features:**
- Mood calendar view
- Quick entry form
- Mood statistics (average, trend, distribution)
- History list with edit/delete
- Mood chart over time

**API Calls:**
- GET `/api/mood/` - List ratings
- POST `/api/mood/` - Create
- PUT `/api/mood/{date}` - Update
- DELETE `/api/mood/{date}` - Delete
- GET `/api/mood/stats/summary` - Statistics

### History Page
**Features:**
- Health metrics table/chart
- Burnout risk history
- Filter by date range
- Export data (CSV)

**API Calls:**
- GET `/api/health/metrics` - Health data
- GET `/api/health/burnout/history` - Risk history

### Insights Page
**Features:**
- List of recent AI insights
- Generate new insight button (with type selection)
- Insight detail view
- Feedback buttons (helpful/not helpful)

**API Calls:**
- GET `/api/health/insights` - List insights
- POST `/api/health/insights/generate` - Generate new

### Settings Page
**Features:**
- WHOOP connection management
- Account settings
- Data preferences
- Logout button

**API Calls:**
- GET `/api/whoop/connection` - Connection status
- POST `/api/whoop/auth/authorize` - Start OAuth
- DELETE `/api/whoop/connection` - Disconnect

## Custom Hooks

### useDashboard
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';

export function useDashboard() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => apiClient.getDashboard(),
    refetchInterval: 60000, // Refresh every minute
  });

  const syncMutation = useMutation({
    mutationFn: () => apiClient.syncWHOOP(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  return {
    dashboard: data,
    isLoading,
    error,
    sync: syncMutation.mutate,
    isSyncing: syncMutation.isPending,
  };
}
```

### useMood
```typescript
export function useMood() {
  const queryClient = useQueryClient();

  const { data: moods } = useQuery({
    queryKey: ['moods'],
    queryFn: () => apiClient.getMoodRatings(),
  });

  const createMutation = useMutation({
    mutationFn: (data: { date: string; rating: number; notes?: string }) =>
      apiClient.createMoodRating(data.date, data.rating, data.notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['moods'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  return {
    moods,
    createMood: createMutation.mutate,
    isCreating: createMutation.isPending,
  };
}
```

## Routing Structure

```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/mood" element={<Mood />} />
              <Route path="/history" element={<History />} />
              <Route path="/insights" element={<Insights />} />
              <Route path="/settings" element={<Settings />} />
            </Route>

            <Route path="/" element={<Navigate to="/dashboard" />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
```

## State Management Strategy

### React Query for Server State
- Dashboard data
- Health metrics
- Mood ratings
- Burnout scores
- AI insights
- WHOOP connection status

**Benefits:**
- Automatic caching
- Background refetching
- Optimistic updates
- Loading/error states

### React Context for Auth
- User session
- JWT tokens
- Login/logout actions

### Local State for UI
- Form inputs
- Modal visibility
- Selected filters
- Chart options

## API Integration Patterns

### Authentication Flow
```typescript
// 1. Login
const response = await apiClient.signin(email, password);
// Token automatically stored in localStorage
// Auth header set for all future requests

// 2. Protected requests
const dashboard = await apiClient.getDashboard();
// Uses stored token automatically

// 3. Token refresh
// Automatic via axios interceptor
// Refreshes on 401, retries failed request

// 4. Logout
await apiClient.signout();
// Clears tokens, redirects to login
```

### Data Fetching Pattern
```typescript
// Using React Query
const { data, isLoading, error, refetch } = useQuery({
  queryKey: ['dashboard'],
  queryFn: () => apiClient.getDashboard(),
  staleTime: 30000, // 30 seconds
  refetchInterval: 60000, // 1 minute
});

if (isLoading) return <Loading />;
if (error) return <Error message={error.message} />;
return <Dashboard data={data} onRefresh={refetch} />;
```

### Mutation Pattern
```typescript
const mutation = useMutation({
  mutationFn: (data) => apiClient.createMoodRating(data.date, data.rating, data.notes),
  onSuccess: () => {
    // Invalidate related queries
    queryClient.invalidateQueries({ queryKey: ['moods'] });
    queryClient.invalidateQueries({ queryKey: ['dashboard'] });

    // Show success toast
    toast.success('Mood rating saved!');
  },
  onError: (error) => {
    toast.error('Failed to save mood rating');
  },
});
```

## UI/UX Considerations

### Loading States
- Skeleton loaders for content
- Spinner for buttons
- Progress bars for sync operations
- Shimmer effect for placeholders

### Error Handling
- Toast notifications for errors
- Inline form validation
- Error boundaries for crashes
- Retry buttons for failed requests

### Responsive Design
- Mobile-first approach
- Collapsible sidebar on mobile
- Touch-friendly buttons
- Swipe gestures for navigation

### Accessibility
- ARIA labels
- Keyboard navigation
- Focus management
- Color contrast compliance

## Performance Optimizations

1. **Code Splitting**
   - Route-based splitting
   - Lazy load components
   - Dynamic imports

2. **Caching Strategy**
   - React Query cache
   - LocalStorage for tokens
   - Service worker (future)

3. **Optimistic Updates**
   - Instant UI updates
   - Rollback on failure
   - Optimistic mood entries

4. **Image Optimization**
   - Lazy loading
   - WebP format
   - Responsive images

## Implementation Priority

### Phase 1: Core (Days 11-12)
1. ✅ API client with authentication
2. ✅ Auth context and protected routes
3. ✅ Login/signup pages
4. ✅ Basic dashboard layout
5. ✅ Metrics display

### Phase 2: Features (Day 13)
6. Mood entry and history
7. Health metrics charts
8. Burnout risk visualization
9. WHOOP connection UI

### Phase 3: Polish (Day 14)
10. AI insights display
11. Settings page
12. Error handling
13. Loading states
14. Mobile responsiveness

## Testing Strategy

### Unit Tests
- Component rendering
- Hook logic
- Utility functions
- API client methods

### Integration Tests
- Auth flow
- Data fetching
- Form submissions
- Navigation

### E2E Tests
- Complete user journeys
- Login → Sync → View Dashboard
- Create mood → View history
- Generate insight → View recommendations

## Deployment

### Environment Variables
```bash
VITE_API_URL=https://api.respire.app
VITE_WHOOP_REDIRECT_URI=https://respire.app/auth/whoop/callback
```

### Build Command
```bash
npm run build
# Outputs to dist/
```

### Vercel Configuration
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "installCommand": "npm install"
}
```

## Conclusion

This frontend specification provides a complete, production-ready React application that integrates seamlessly with all 21 backend API endpoints. The architecture emphasizes:

- **Type Safety**: Full TypeScript coverage
- **Performance**: React Query caching and optimistic updates
- **User Experience**: Responsive design and intuitive UI
- **Maintainability**: Clear component structure and separation of concerns
- **Scalability**: Easy to extend with new features

The implementation demonstrates modern React best practices and would be impressive to FAANG recruiters as a portfolio piece.