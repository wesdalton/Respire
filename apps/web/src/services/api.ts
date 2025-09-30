import axios, { AxiosInstance } from 'axios';
import type { AuthResponse, DashboardData, HealthMetric, MoodRating, BurnoutScore, AIInsight, WHOOPConnection } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load token from localStorage
    this.token = localStorage.getItem('access_token');
    if (this.token) {
      this.setAuthHeader(this.token);
    }

    // Add response interceptor for token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const { data } = await this.client.post<AuthResponse>('/auth/refresh', {
                refresh_token: refreshToken,
              });
              this.setToken(data.access_token, data.refresh_token);
              // Retry original request
              error.config.headers.Authorization = `Bearer ${data.access_token}`;
              return this.client.request(error.config);
            } catch {
              // Refresh failed, clear tokens
              this.clearToken();
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(accessToken: string, refreshToken?: string) {
    this.token = accessToken;
    localStorage.setItem('access_token', accessToken);
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }
    this.setAuthHeader(accessToken);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    delete this.client.defaults.headers.common['Authorization'];
  }

  private setAuthHeader(token: string) {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  // Auth endpoints
  async signup(email: string, password: string, firstName?: string, lastName?: string) {
    const { data } = await this.client.post<AuthResponse>('/auth/signup', {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
    });
    this.setToken(data.access_token, data.refresh_token);
    return data;
  }

  async signin(email: string, password: string) {
    const { data } = await this.client.post<AuthResponse>('/auth/signin', {
      email,
      password,
    });
    this.setToken(data.access_token, data.refresh_token);
    return data;
  }

  async signout() {
    try {
      await this.client.post('/auth/signout');
    } finally {
      this.clearToken();
    }
  }

  // Dashboard
  async getDashboard(): Promise<DashboardData> {
    const { data } = await this.client.get<DashboardData>('/health/dashboard');
    return data;
  }

  // Health metrics
  async getHealthMetrics(startDate?: string, endDate?: string, limit = 30): Promise<HealthMetric[]> {
    const { data } = await this.client.get<HealthMetric[]>('/health/metrics', {
      params: { start_date: startDate, end_date: endDate, limit },
    });
    return data;
  }

  // Mood ratings
  async getMoodRatings(startDate?: string, endDate?: string, limit = 30): Promise<MoodRating[]> {
    const { data } = await this.client.get<MoodRating[]>('/mood/', {
      params: { start_date: startDate, end_date: endDate, limit },
    });
    return data;
  }

  async createMoodRating(date: string, rating: number, notes?: string): Promise<MoodRating> {
    const { data} = await this.client.post<MoodRating>('/mood/', {
      date,
      rating,
      notes,
    });
    return data;
  }

  async updateMoodRating(date: string, rating?: number, notes?: string): Promise<MoodRating> {
    const { data } = await this.client.put<MoodRating>(`/mood/${date}`, {
      rating,
      notes,
    });
    return data;
  }

  async deleteMoodRating(date: string): Promise<void> {
    await this.client.delete(`/mood/${date}`);
  }

  async getMoodStats(days = 30) {
    const { data } = await this.client.get('/mood/stats/summary', {
      params: { days },
    });
    return data;
  }

  // Burnout
  async calculateBurnoutRisk(days = 14): Promise<BurnoutScore> {
    const { data } = await this.client.post<BurnoutScore>('/health/burnout/calculate', null, {
      params: { days },
    });
    return data;
  }

  async getBurnoutHistory(limit = 30): Promise<BurnoutScore[]> {
    const { data } = await this.client.get<BurnoutScore[]>('/health/burnout/history', {
      params: { limit },
    });
    return data;
  }

  // AI Insights
  async generateInsight(insightType = 'weekly_summary', days = 14): Promise<AIInsight> {
    const { data } = await this.client.post<AIInsight>('/health/insights/generate', null, {
      params: { insight_type: insightType, days },
    });
    return data;
  }

  async getInsights(limit = 10): Promise<AIInsight[]> {
    const { data } = await this.client.get<AIInsight[]>('/health/insights', {
      params: { limit },
    });
    return data;
  }

  // WHOOP
  async getWHOOPConnection(): Promise<WHOOPConnection> {
    const { data } = await this.client.get<WHOOPConnection>('/whoop/connection');
    return data;
  }

  async getWHOOPAuthURL(redirectUri: string): Promise<{ authorization_url: string; state: string }> {
    const { data } = await this.client.post('/whoop/auth/authorize', {
      redirect_uri: redirectUri,
    });
    return data;
  }

  async connectWHOOP(code: string, redirectUri: string): Promise<WHOOPConnection> {
    const { data } = await this.client.post<WHOOPConnection>('/whoop/auth/callback', {
      code,
      redirect_uri: redirectUri,
    });
    return data;
  }

  async syncWHOOP(startDate?: string, endDate?: string) {
    const { data } = await this.client.post('/whoop/sync/manual', null, {
      params: { start_date: startDate, end_date: endDate },
    });
    return data;
  }

  async disconnectWHOOP(): Promise<void> {
    await this.client.delete('/whoop/connection');
  }
}

export const apiClient = new APIClient();