// 目标管理页面
import React, { useState } from 'react';
import { Plus, Target, Calendar, Clock, TrendingUp } from 'lucide-react';
import { PageLoading, LoadingButton } from '../components/Loading';
import { useGoals, useCreateGoal, useUpdateGoal, useDeleteGoal } from '../hooks/useApi';
import { format, parseISO, addDays } from 'date-fns';
import type { GoalCreate, Priority, Status } from '../types/api';

const Goals: React.FC = () => {
  const [isAddingGoal, setIsAddingGoal] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('active');
  
  const { data: goalsData, isLoading, refetch } = useGoals({ 
    status: statusFilter === 'all' ? undefined : statusFilter 
  });
  
  const createGoal = useCreateGoal();
  const updateGoal = useUpdateGoal();
  const deleteGoal = useDeleteGoal();

  // 表单状态
  const [formData, setFormData] = useState<GoalCreate>({
    title: '',
    deadline: format(addDays(new Date(), 7), 'yyyy-MM-dd'),
    estimated_time: 120,
    priority: 'Medium' as Priority
  });

  const handleAddGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) return;

    try {
      await createGoal.mutateAsync(formData);
      setFormData({
        title: '',
        deadline: format(addDays(new Date(), 7), 'yyyy-MM-dd'),
        estimated_time: 120,
        priority: 'Medium' as Priority
      });
      setIsAddingGoal(false);
      refetch();
    } catch (error) {
      // Error is handled by the hook
    }
  };

  const handleUpdateStatus = async (goalId: string, status: Status) => {
    try {
      await updateGoal.mutateAsync({
        goalId,
        goalData: { status }
      });
      refetch();
    } catch (error) {
      // Error is handled by the hook
    }
  };

  const handleDeleteGoal = async (goalId: string) => {
    if (!confirm('确定要删除这个目标吗？')) return;
    
    try {
      await deleteGoal.mutateAsync(goalId);
      refetch();
    } catch (error) {
      // Error is handled by the hook
    }
  };

  const getStatusColor = (status: Status) => {
    switch (status) {
      case 'Planned': return 'bg-gray-100 text-gray-800';
      case 'In Progress': return 'bg-blue-100 text-blue-800';
      case 'Completed': return 'bg-green-100 text-green-800';
      case 'Abandoned': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: Priority) => {
    switch (priority) {
      case 'High': return 'bg-red-100 text-red-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'Low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return <PageLoading />;
  }

  return (
    <div className="space-y-6">
      {/* 页面标题和操作 */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            目标管理
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            创建和管理您的目标，追踪完成进度
          </p>
        </div>
        <div className="mt-4 flex space-x-3 md:ml-4 md:mt-0">
          <button
            onClick={() => setIsAddingGoal(true)}
            className="btn btn-primary inline-flex items-center"
          >
            <Plus className="mr-2 h-4 w-4" />
            新建目标
          </button>
        </div>
      </div>

      {/* 筛选器 */}
      <div className="card">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">状态筛选:</span>
          {[
            { key: 'active', label: '活跃中', count: goalsData?.active_count },
            { key: 'all', label: '全部', count: goalsData?.total },
            { key: 'Completed', label: '已完成' },
            { key: 'Abandoned', label: '已放弃' }
          ].map((filter) => (
            <button
              key={filter.key}
              onClick={() => setStatusFilter(filter.key)}
              className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                statusFilter === filter.key
                  ? 'bg-primary-100 text-primary-800'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {filter.label}
              {filter.count !== undefined && (
                <span className="ml-1">({filter.count})</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* 添加目标表单 */}
      {isAddingGoal && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">创建新目标</h3>
          <form onSubmit={handleAddGoal} className="space-y-4">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                目标标题
              </label>
              <input
                type="text"
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="例如：学习Python编程"
                className="input mt-1"
                autoFocus
                required
              />
            </div>
            
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div>
                <label htmlFor="deadline" className="block text-sm font-medium text-gray-700">
                  截止日期
                </label>
                <input
                  type="date"
                  id="deadline"
                  value={formData.deadline}
                  onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                  className="input mt-1"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="estimated_time" className="block text-sm font-medium text-gray-700">
                  预估时长(分钟)
                </label>
                <input
                  type="number"
                  id="estimated_time"
                  value={formData.estimated_time}
                  onChange={(e) => setFormData({ ...formData, estimated_time: parseInt(e.target.value) })}
                  min="1"
                  className="input mt-1"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
                  优先级
                </label>
                <select
                  id="priority"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value as Priority })}
                  className="input mt-1"
                >
                  <option value="High">高</option>
                  <option value="Medium">中</option>
                  <option value="Low">低</option>
                </select>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setIsAddingGoal(false);
                  setFormData({
                    title: '',
                    deadline: format(addDays(new Date(), 7), 'yyyy-MM-dd'),
                    estimated_time: 120,
                    priority: 'Medium' as Priority
                  });
                }}
                className="btn btn-secondary"
              >
                取消
              </button>
              <LoadingButton
                type="submit"
                loading={createGoal.isPending}
                className="btn-primary"
              >
                创建目标
              </LoadingButton>
            </div>
          </form>
        </div>
      )}

      {/* 目标列表 */}
      <div className="space-y-4">
        {goalsData?.goals && goalsData.goals.length > 0 ? (
          goalsData.goals.map((goal) => (
            <div key={goal.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-medium text-gray-900">
                      {goal.title}
                    </h3>
                    <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${getStatusColor(goal.status)}`}>
                      {goal.status === 'Planned' ? '计划中' :
                       goal.status === 'In Progress' ? '进行中' :
                       goal.status === 'Completed' ? '已完成' : '已放弃'}
                    </span>
                    <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${getPriorityColor(goal.priority)}`}>
                      {goal.priority === 'High' ? '高优先级' :
                       goal.priority === 'Medium' ? '中优先级' : '低优先级'}
                    </span>
                  </div>
                  
                  {/* 进度条 */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                      <span>进度</span>
                      <span>{goal.actual_time}/{goal.estimated_time} 分钟 ({goal.progress}%)</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          goal.progress >= 100 ? 'bg-green-600' : 'bg-primary-600'
                        }`}
                        style={{ width: `${Math.min(goal.progress, 100)}%` }}
                      />
                    </div>
                  </div>
                  
                  {/* 详细信息 */}
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <Calendar className="mr-1 h-4 w-4" />
                      截止: {format(parseISO(goal.deadline), 'MM/dd')}
                    </div>
                    <div className="flex items-center">
                      <Clock className="mr-1 h-4 w-4" />
                      预估: {Math.floor(goal.estimated_time / 60)}h {goal.estimated_time % 60}m
                    </div>
                    <div className="flex items-center">
                      <TrendingUp className="mr-1 h-4 w-4" />
                      已投入: {Math.floor(goal.actual_time / 60)}h {goal.actual_time % 60}m
                    </div>
                  </div>
                </div>
                
                {/* 操作按钮 */}
                <div className="flex items-center space-x-2 ml-4">
                  {goal.status === 'Planned' && (
                    <button
                      onClick={() => handleUpdateStatus(goal.id, 'In Progress')}
                      className="text-blue-600 hover:text-blue-900 text-sm"
                      disabled={updateGoal.isPending}
                    >
                      开始
                    </button>
                  )}
                  {goal.status === 'In Progress' && (
                    <button
                      onClick={() => handleUpdateStatus(goal.id, 'Completed')}
                      className="text-green-600 hover:text-green-900 text-sm"
                      disabled={updateGoal.isPending}
                    >
                      完成
                    </button>
                  )}
                  <button
                    onClick={() => handleDeleteGoal(goal.id)}
                    className="text-red-600 hover:text-red-900 text-sm"
                    disabled={deleteGoal.isPending}
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12">
            <Target className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">暂无目标</h3>
            <p className="mt-1 text-sm text-gray-500">
              创建您的第一个目标来开始时间管理之旅
            </p>
            <div className="mt-6">
              <button
                onClick={() => setIsAddingGoal(true)}
                className="btn btn-primary inline-flex items-center"
              >
                <Plus className="mr-2 h-4 w-4" />
                新建目标
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Goals;