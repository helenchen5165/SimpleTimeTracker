// API响应类型定义

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
  };
}

// 用户相关类型
export interface User {
  id: string;
  nickname: string;
  avatar: string;
  created_at: string;
}

export interface LoginRequest {
  code: string;
  user_info: {
    nickName: string;
    avatarUrl: string;
  };
}

export interface LoginResponse {
  token: string;
  user: User;
}

// 目标相关类型
export type Priority = 'High' | 'Medium' | 'Low';
export type Status = 'Planned' | 'In Progress' | 'Completed' | 'Abandoned';

export interface Goal {
  id: string;
  title: string;
  deadline: string; // ISO date string
  estimated_time: number; // minutes
  actual_time: number; // minutes  
  progress: number; // 0-100
  priority: Priority;
  status: Status;
  created_at: string;
  updated_at?: string;
}

export interface GoalCreate {
  title: string;
  deadline: string;
  estimated_time: number;
  priority: Priority;
}

export interface GoalUpdate {
  title?: string;
  deadline?: string;
  estimated_time?: number;
  priority?: Priority;
  status?: Status;
}

export interface GoalListResponse {
  goals: Goal[];
  total: number;
  active_count: number;
}

// 时间记录相关类型
export type Category = '生产' | '投资' | '支出';
export type ParsingMethod = 'Claude' | 'Rules';

export interface TimeRecord {
  id: string;
  start_time: string; // ISO datetime string
  end_time: string; // ISO datetime string
  duration: number; // minutes
  activity: string;
  category: Category;
  description: string;
  confidence: number; // 0-100
  parsing_method: ParsingMethod;
  matched_goal?: {
    id: string;
    title: string;
    progress_after?: number;
    progress_percentage?: number;
  };
  created_at: string;
}

export interface TimeRecordCreate {
  input_text: string;
  manual_goal_id?: string;
}

export interface TimeRecordListResponse {
  records: TimeRecord[];
  total: number;
  total_duration: number;
}

// 报告相关类型
export interface CategoryStats {
  duration: number;
  percentage: number;
}

export interface ActivityStats {
  activity: string;
  duration: number;
}

export interface GoalProgress {
  goal_id: string;
  title: string;
  progress: number; // actual time
  estimated: number;
  percentage: number;
}

export interface DailyReport {
  report_date: string;
  total_records: number;
  total_duration: number;
  efficiency_rate: number;
  category_stats: Record<string, CategoryStats>;
  activity_stats: ActivityStats[];
  goal_progress: GoalProgress[];
}

export interface WeeklyReport {
  week: string;
  date_range: string[];
  total_duration: number;
  efficiency_rate: number;
  daily_breakdown: Array<{
    breakdown_date: string;
    duration: number;
  }>;
  category_summary: Record<string, CategoryStats>;
  completed_goals: Array<{
    title: string;
    estimated_time: number;
    actual_time: number;
  }>;
}

// Notion 集成相关类型
export interface NotionDatabase {
  id: string;
  title: string;
  url: string;
  created_time: string;
  last_edited_time: string;
  properties: Record<string, {
    type: string;
    name: string;
  }>;
}

export interface NotionPage {
  id: string;
  title: string;
  url: string;
  created_time: string;
  last_edited_time: string;
  properties: Record<string, any>;
}

export interface NotionConnection {
  token: string;
  connected_at: string;
  databases_count: number;
}

export interface NotionSetupStep {
  step: number;
  title: string;
  description: string;
  action: string;
}