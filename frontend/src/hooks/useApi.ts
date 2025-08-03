// React Query hooks for API calls
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import apiService from '../services/api';
import type {
  GoalCreate,
  GoalUpdate,
  TimeRecordCreate,
} from '../types/api';

// =============== 目标管理 hooks ===============

export const useGoals = (params?: { status?: string; deadline?: string }) => {
  return useQuery({
    queryKey: ['goals', params],
    queryFn: () => apiService.getGoals(params),
    staleTime: 5 * 60 * 1000, // 5分钟
  });
};

export const useGoal = (goalId: string) => {
  return useQuery({
    queryKey: ['goal', goalId],
    queryFn: () => apiService.getGoal(goalId),
    enabled: !!goalId,
  });
};

export const useCreateGoal = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (goalData: GoalCreate) => apiService.createGoal(goalData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      toast.success('目标创建成功！');
    },
    onError: (error: Error) => {
      toast.error(error.message || '创建目标失败');
    },
  });
};

export const useUpdateGoal = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ goalId, goalData }: { goalId: string; goalData: GoalUpdate }) =>
      apiService.updateGoal(goalId, goalData),
    onSuccess: (_, { goalId }) => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      queryClient.invalidateQueries({ queryKey: ['goal', goalId] });
      toast.success('目标更新成功！');
    },
    onError: (error: Error) => {
      toast.error(error.message || '更新目标失败');
    },
  });
};

export const useDeleteGoal = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (goalId: string) => apiService.deleteGoal(goalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      toast.success('目标删除成功！');
    },
    onError: (error: Error) => {
      toast.error(error.message || '删除目标失败');
    },
  });
};

// =============== 时间记录 hooks ===============

export const useTimeRecords = (params?: {
  target_date?: string;
  limit?: number;
  offset?: number;
}) => {
  return useQuery({
    queryKey: ['timeRecords', params],
    queryFn: () => apiService.getTimeRecords(params),
    staleTime: 2 * 60 * 1000, // 2分钟
  });
};

export const useTimeRecord = (recordId: string) => {
  return useQuery({
    queryKey: ['timeRecord', recordId],
    queryFn: () => apiService.getTimeRecord(recordId),
    enabled: !!recordId,
  });
};

export const useCreateTimeRecord = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (recordData: TimeRecordCreate) => apiService.createTimeRecord(recordData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timeRecords'] });
      queryClient.invalidateQueries({ queryKey: ['goals'] }); // 刷新目标进度
      queryClient.invalidateQueries({ queryKey: ['dailyReport'] });
      toast.success('时间记录创建成功！');
    },
    onError: (error: Error) => {
      toast.error(error.message || '创建时间记录失败');
    },
  });
};

export const useUpdateTimeRecord = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ recordId, recordData }: { recordId: string; recordData: any }) =>
      apiService.updateTimeRecord(recordId, recordData),
    onSuccess: (_, { recordId }) => {
      queryClient.invalidateQueries({ queryKey: ['timeRecords'] });
      queryClient.invalidateQueries({ queryKey: ['timeRecord', recordId] });
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      toast.success('时间记录更新成功！');
    },
    onError: (error: Error) => {
      toast.error(error.message || '更新时间记录失败');
    },
  });
};

export const useDeleteTimeRecord = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (recordId: string) => apiService.deleteTimeRecord(recordId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timeRecords'] });
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      toast.success('时间记录删除成功！');
    },
    onError: (error: Error) => {
      toast.error(error.message || '删除时间记录失败');
    },
  });
};

// =============== 报告统计 hooks ===============

export const useDailyReport = (date?: string) => {
  return useQuery({
    queryKey: ['dailyReport', date],
    queryFn: () => apiService.getDailyReport(date),
    staleTime: 10 * 60 * 1000, // 10分钟
  });
};

export const useWeeklyReport = (weekDate?: string) => {
  return useQuery({
    queryKey: ['weeklyReport', weekDate],
    queryFn: () => apiService.getWeeklyReport(weekDate),
    staleTime: 30 * 60 * 1000, // 30分钟
  });
};

export const useSummaryStats = () => {
  return useQuery({
    queryKey: ['summaryStats'],
    queryFn: () => apiService.getSummaryStats(),
    staleTime: 5 * 60 * 1000, // 5分钟
  });
};

// =============== 仪表板 hooks ===============

export const useTodayOverview = () => {
  return useQuery({
    queryKey: ['todayOverview'],
    queryFn: () => apiService.getTodayOverview(),
    staleTime: 2 * 60 * 1000, // 2分钟
    refetchInterval: 5 * 60 * 1000, // 每5分钟自动刷新
  });
};

export const useWeeklySummary = () => {
  return useQuery({
    queryKey: ['weeklySummary'],
    queryFn: () => apiService.getWeeklySummary(),
    staleTime: 10 * 60 * 1000, // 10分钟
  });
};