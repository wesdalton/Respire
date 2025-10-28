import axios, { type AxiosInstance } from 'axios';
import type { AuthResponse, DashboardData, HealthMetric, MoodRating, BurnoutScore, AIInsight, WHOOPConnection, OuraConnection } from '../types';
import DemoDataService from './DemoDataService';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
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

  private isDemoMode(): boolean {
    return localStorage.getItem('demo_mode') === 'active';
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
    return !!this.token || this.isDemoMode();
  }

  // Auth endpoints
  async signup(email: string, password: string, firstName?: string, lastName?: string, profilePictureUrl?: string) {
    // Demo mode doesn't support signup
    if (this.isDemoMode()) {
      throw new Error('Signup is not available in demo mode. Please exit demo to create an account.');
    }
    const { data } = await this.client.post<any>('/auth/signup', {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
      profile_picture_url: profilePictureUrl,
    });

    // Check if email confirmation is required
    if (data.requires_confirmation) {
      // Return the response without setting tokens
      return data;
    }

    // Auto-confirmed, set tokens
    this.setToken(data.access_token, data.refresh_token);
    return data;
  }

  async signin(email: string, password: string) {
    // Demo mode doesn't support signin
    if (this.isDemoMode()) {
      throw new Error('Signin is not available in demo mode.');
    }
    const { data } = await this.client.post<AuthResponse>('/auth/signin', {
      email,
      password,
    });
    this.setToken(data.access_token, data.refresh_token);
    return data;
  }

  async confirmEmail(tokenHash: string, type: string) {
    const { data } = await this.client.post('/auth/confirm', {
      token_hash: tokenHash,
      type,
    });
    return data;
  }

  async signout() {
    // Demo mode: just clear demo flag
    if (this.isDemoMode()) {
      localStorage.removeItem('demo_mode');
      DemoDataService.clear();
      return;
    }
    try {
      await this.client.post('/auth/signout');
    } finally {
      this.clearToken();
    }
  }

  async getCurrentUser() {
    if (this.isDemoMode()) {
      return DemoDataService.getCurrentUser();
    }
    const { data } = await this.client.get('/auth/me');
    return data;
  }

  async updateProfile(profile: { first_name?: string; last_name?: string; profile_picture_url?: string }) {
    if (this.isDemoMode()) {
      return DemoDataService.updateProfile(profile);
    }
    const { data } = await this.client.put('/auth/me', profile);
    return data;
  }

  async getOAuthURL(provider: string): Promise<{ url: string; provider: string }> {
    const { data } = await this.client.get(`/auth/oauth/${provider}/url`);
    return data;
  }

  async uploadProfilePicture(file: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await this.client.post<{ url: string }>('/auth/upload-profile-picture', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    // Return the URL directly (already a full URL from Supabase Storage)
    return data.url;
  }

  // Dashboard
  async getDashboard(selectedDate?: string): Promise<DashboardData> {
    if (this.isDemoMode()) {
      return DemoDataService.getDashboard();
    }
    const params = selectedDate ? { selected_date: selectedDate } : {};
    const { data } = await this.client.get<DashboardData>('/health/dashboard', { params });
    return data;
  }

  // Health metrics
  async getHealthMetrics(startDate?: string, endDate?: string, limit = 30): Promise<HealthMetric[]> {
    if (this.isDemoMode()) {
      return DemoDataService.getHealthMetrics(startDate, endDate, limit);
    }
    const { data } = await this.client.get<HealthMetric[]>('/health/metrics', {
      params: { start_date: startDate, end_date: endDate, limit },
    });
    return data;
  }

  // Mood ratings
  async getMoodRatings(startDate?: string, endDate?: string, limit = 30): Promise<MoodRating[]> {
    if (this.isDemoMode()) {
      return DemoDataService.getMoodRatings(startDate, endDate, limit);
    }
    const { data } = await this.client.get<MoodRating[]>('/mood/', {
      params: { start_date: startDate, end_date: endDate, limit },
    });
    return data;
  }

  async createMoodRating(params: { date: string; rating: number; notes?: string }): Promise<MoodRating> {
    if (this.isDemoMode()) {
      return DemoDataService.createMoodRating(params);
    }
    const { data } = await this.client.post<MoodRating>('/mood/', params);
    return data;
  }

  async updateMoodRating(date: string, rating?: number, notes?: string): Promise<MoodRating> {
    if (this.isDemoMode()) {
      return DemoDataService.updateMoodRating(date, rating, notes);
    }
    const { data } = await this.client.put<MoodRating>(`/mood/${date}`, {
      rating,
      notes,
    });
    return data;
  }

  async deleteMoodRating(date: string): Promise<void> {
    if (this.isDemoMode()) {
      return DemoDataService.deleteMoodRating(date);
    }
    await this.client.delete(`/mood/${date}`);
  }

  async getMoodStats(days = 30) {
    if (this.isDemoMode()) {
      return DemoDataService.getMoodStats(days);
    }
    const { data } = await this.client.get('/mood/stats/summary', {
      params: { days },
    });
    return data;
  }

  // Burnout
  async calculateBurnoutRisk(days = 14): Promise<BurnoutScore> {
    if (this.isDemoMode()) {
      return DemoDataService.calculateBurnoutRisk(days);
    }
    const { data } = await this.client.post<BurnoutScore>('/health/burnout/calculate', null, {
      params: { days },
    });
    return data;
  }

  async getBurnoutHistory(startDate?: string, endDate?: string, limit = 30): Promise<BurnoutScore[]> {
    if (this.isDemoMode()) {
      return DemoDataService.getBurnoutHistory(startDate, endDate, limit);
    }
    const { data } = await this.client.get<BurnoutScore[]>('/health/burnout/history', {
      params: { start_date: startDate, end_date: endDate, limit },
    });
    return data;
  }

  // AI Insights
  async generateInsight(insightType = 'weekly_summary', days = 14): Promise<AIInsight> {
    if (this.isDemoMode()) {
      return DemoDataService.generateInsight(insightType, days);
    }
    const { data } = await this.client.post<AIInsight>('/health/insights/generate', null, {
      params: { insight_type: insightType, days },
    });
    return data;
  }

  async getInsights(limit = 10): Promise<AIInsight[]> {
    if (this.isDemoMode()) {
      return DemoDataService.getInsights(limit);
    }
    const { data } = await this.client.get<AIInsight[]>('/health/insights', {
      params: { limit },
    });
    return data;
  }

  async updateInsightFeedback(insightId: string, helpful: boolean, feedback?: string): Promise<AIInsight> {
    if (this.isDemoMode()) {
      return DemoDataService.updateInsightFeedback(insightId, helpful, feedback);
    }
    const { data } = await this.client.patch<AIInsight>(`/health/insights/${insightId}/feedback`, null, {
      params: { helpful, feedback },
    });
    return data;
  }

  async deleteInsight(insightId: string): Promise<{ message: string }> {
    if (this.isDemoMode()) {
      return DemoDataService.deleteInsight(insightId);
    }
    const { data } = await this.client.delete<{ message: string }>(`/health/insights/${insightId}`);
    return data;
  }

  async deleteAllUserData(): Promise<{ message: string }> {
    const { data } = await this.client.delete<{ message: string }>('/auth/delete-all-data');
    return data;
  }

  // WHOOP
  async getWHOOPConnection(): Promise<WHOOPConnection> {
    if (this.isDemoMode()) {
      return DemoDataService.getWHOOPConnection();
    }
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
    if (this.isDemoMode()) {
      return DemoDataService.syncWHOOP(startDate, endDate);
    }
    const { data } = await this.client.post('/whoop/sync/manual', null, {
      params: { start_date: startDate, end_date: endDate },
    });
    return data;
  }

  async disconnectWHOOP(): Promise<void> {
    if (this.isDemoMode()) {
      return DemoDataService.disconnectWHOOP();
    }
    await this.client.delete('/whoop/connection');
  }

  // Oura endpoints
  async getOuraConnection(): Promise<OuraConnection | null> {
    try {
      const { data } = await this.client.get('/oura/connection');
      return data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async getOuraAuthURL(redirectUri: string) {
    const { data } = await this.client.post('/oura/auth/authorize', {
      redirect_uri: redirectUri,
    });
    return data;
  }

  async connectOura(code: string, redirectUri: string): Promise<OuraConnection> {
    const { data } = await this.client.post('/oura/auth/callback', {
      code,
      redirect_uri: redirectUri,
    });
    return data;
  }

  async syncOura(startDate?: string, endDate?: string) {
    const { data } = await this.client.post('/oura/sync/manual', null, {
      params: { start_date: startDate, end_date: endDate },
    });
    return data;
  }

  async disconnectOura(): Promise<void> {
    await this.client.post('/oura/disconnect');
  }

  // User Preferences
  async getUserPreferences() {
    const { data } = await this.client.get('/auth/preferences');
    return data;
  }

  async updateUserPreferences(updates: { primary_data_source?: 'whoop' | 'oura' }) {
    const { data } = await this.client.patch('/auth/preferences', updates);
    return data;
  }
}

export const apiClient = new APIClient();