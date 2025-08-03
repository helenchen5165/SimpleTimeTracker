// API服务层
import axios, { type AxiosInstance, type AxiosResponse } from 'axios';
import type {
  ApiResponse,
  LoginRequest,
  LoginResponse,
  Goal,
  GoalCreate,
  GoalUpdate,
  GoalListResponse,
  TimeRecord,
  TimeRecordCreate,
  TimeRecordListResponse,
  DailyReport,
  WeeklyReport,
  NotionDatabase,
  NotionPage,
  NotionSetupStep,
} from '../types/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/v1',
      timeout: 10000,
    });

    // 请求拦截器 - 添加认证token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 响应拦截器 - 处理错误和token过期
    this.api.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        return response;
      },
      async (error) => {
        if (error.response?.status === 401) {
          // Token过期，清除本地存储并跳转到登录页
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_info');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // =============== 认证相关 ===============

  async login(loginData: LoginRequest): Promise<LoginResponse> {
    const response = await this.api.post<ApiResponse<LoginResponse>>('/auth/wechat/login', loginData);
    if (response.data.success && response.data.data) {
      // 保存token和用户信息
      localStorage.setItem('auth_token', response.data.data.token);
      localStorage.setItem('user_info', JSON.stringify(response.data.data.user));
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '登录失败');
  }

  async refreshToken(): Promise<string> {
    const response = await this.api.post<ApiResponse<{ token: string }>>('/auth/refresh');
    if (response.data.success && response.data.data) {
      localStorage.setItem('auth_token', response.data.data.token);
      return response.data.data.token;
    }
    throw new Error('Token刷新失败');
  }

  async getCurrentUser(): Promise<any> {
    const response = await this.api.get<ApiResponse>('/auth/me');
    if (response.data.success) {
      return response.data.data;
    }
    throw new Error('获取用户信息失败');
  }

  // =============== 目标管理 ===============

  async getGoals(params?: {
    status?: string;
    deadline?: string;
  }): Promise<GoalListResponse> {
    const response = await this.api.get<ApiResponse<GoalListResponse>>('/goals', { params });
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取目标列表失败');
  }

  async createGoal(goalData: GoalCreate): Promise<Goal> {
    const response = await this.api.post<ApiResponse<Goal>>('/goals', goalData);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '创建目标失败');
  }

  async getGoal(goalId: string): Promise<Goal> {
    const response = await this.api.get<ApiResponse<Goal>>(`/goals/${goalId}`);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取目标详情失败');
  }

  async updateGoal(goalId: string, goalData: GoalUpdate): Promise<Goal> {
    const response = await this.api.put<ApiResponse<Goal>>(`/goals/${goalId}`, goalData);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '更新目标失败');
  }

  async deleteGoal(goalId: string): Promise<void> {
    const response = await this.api.delete<ApiResponse>(`/goals/${goalId}`);
    if (!response.data.success) {
      throw new Error(response.data.error?.message || '删除目标失败');
    }
  }

  // =============== 时间记录 ===============

  async createTimeRecord(recordData: TimeRecordCreate): Promise<TimeRecord> {
    const response = await this.api.post<ApiResponse<TimeRecord>>('/time-records', recordData);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '创建时间记录失败');
  }

  async getTimeRecords(params?: {
    target_date?: string;
    limit?: number;
    offset?: number;
  }): Promise<TimeRecordListResponse> {
    const response = await this.api.get<ApiResponse<TimeRecordListResponse>>('/time-records', { params });
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取时间记录失败');
  }

  async getTimeRecord(recordId: string): Promise<TimeRecord> {
    const response = await this.api.get<ApiResponse<TimeRecord>>(`/time-records/${recordId}`);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取时间记录详情失败');
  }

  async updateTimeRecord(recordId: string, recordData: any): Promise<TimeRecord> {
    const response = await this.api.put<ApiResponse<TimeRecord>>(`/time-records/${recordId}`, recordData);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '更新时间记录失败');
  }

  async deleteTimeRecord(recordId: string): Promise<void> {
    const response = await this.api.delete<ApiResponse>(`/time-records/${recordId}`);
    if (!response.data.success) {
      throw new Error(response.data.error?.message || '删除时间记录失败');
    }
  }

  // =============== 报告统计 ===============

  async getDailyReport(date?: string): Promise<DailyReport> {
    const params = date ? { target_date: date } : undefined;
    const response = await this.api.get<ApiResponse<DailyReport>>('/reports/daily', { params });
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取日报失败');
  }

  async getWeeklyReport(weekDate?: string): Promise<WeeklyReport> {
    const params = weekDate ? { week_date: weekDate } : undefined;
    const response = await this.api.get<ApiResponse<WeeklyReport>>('/reports/weekly', { params });
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取周报失败');
  }

  async getSummaryStats(): Promise<any> {
    const response = await this.api.get<ApiResponse>('/reports/summary');
    if (response.data.success) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取概览统计失败');
  }

  // =============== 仪表板相关 ===============

  async getTodayOverview(): Promise<any> {
    const response = await this.api.get<ApiResponse>('/dashboard/today-overview');
    if (response.data.success) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取今日概览失败');
  }

  async getWeeklySummary(): Promise<any> {
    const response = await this.api.get<ApiResponse>('/dashboard/weekly-summary');
    if (response.data.success) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取周汇总失败');
  }

  // =============== Notion 集成 ===============

  async getNotionSetupGuide(): Promise<{ guide: { title: string; steps: NotionSetupStep[] } }> {
    const response = await this.api.get<ApiResponse>('/notion/setup-guide');
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取设置指南失败');
  }

  async connectNotion(token: string): Promise<{ message: string; databases_count: number; databases: NotionDatabase[] }> {
    const response = await this.api.post<ApiResponse>('/notion/connect', { token });
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || 'Notion 连接失败');
  }

  async getNotionDatabases(token: string): Promise<{ databases: NotionDatabase[]; total: number }> {
    const response = await this.api.get<ApiResponse>(`/notion/databases?token=${encodeURIComponent(token)}`);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取数据库列表失败');
  }

  async getNotionPages(databaseId: string, token: string): Promise<{ pages: NotionPage[]; total: number }> {
    const response = await this.api.get<ApiResponse>(`/notion/databases/${databaseId}/pages?token=${encodeURIComponent(token)}`);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || '获取页面列表失败');
  }
}

// 导出单例
export const apiService = new ApiService();
export default apiService;