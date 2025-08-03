// 首页/仪表板页面
import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, Target, TrendingUp, Plus } from 'lucide-react';
import { PageLoading } from '../components/Loading';
import { useSummaryStats, useGoals, useTimeRecords } from '../hooks/useApi';
import { format } from 'date-fns';

const Dashboard: React.FC = () => {
  const { data: summaryStats, isLoading: summaryLoading } = useSummaryStats();
  const { data: goalsData, isLoading: goalsLoading } = useGoals({ status: 'active' });
  const { data: todayRecords, isLoading: recordsLoading } = useTimeRecords({
    target_date: format(new Date(), 'yyyy-MM-dd'),
    limit: 5
  });

  if (summaryLoading || goalsLoading || recordsLoading) {
    return <PageLoading />;
  }

  const quickStats = [
    {
      name: '今日时长',
      value: `${summaryStats?.today_duration || 0}分钟`,
      change: '+12%',
      changeType: 'positive',
      icon: Clock,
    },
    {
      name: '活跃目标',
      value: goalsData?.active_count || 0,
      change: '+2',
      changeType: 'positive',
      icon: Target,
    },
    {
      name: '本周效率',
      value: `${summaryStats?.avg_daily_efficiency || 0}%`,
      change: '+5.4%',
      changeType: 'positive',
      icon: TrendingUp,
    },
  ];

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            欢迎回来！
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            这是您的时间管理概览
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <Link
            to="/time-records/new"
            className="btn btn-primary inline-flex items-center"
          >
            <Plus className="mr-2 h-4 w-4" />
            添加记录
          </Link>
        </div>
      </div>

      {/* 快速统计 */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {quickStats.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.name} className="card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Icon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {item.name}
                    </dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">
                        {item.value}
                      </div>
                      <div
                        className={`ml-2 flex items-baseline text-sm font-semibold ${
                          item.changeType === 'positive'
                            ? 'text-green-600'
                            : 'text-red-600'
                        }`}
                      >
                        {item.change}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* 今日目标 */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">今日目标</h3>
            <Link
              to="/goals"
              className="text-sm text-primary-600 hover:text-primary-900"
            >
              查看全部
            </Link>
          </div>
          <div className="space-y-3">
            {goalsData?.goals.slice(0, 3).map((goal) => (
              <div key={goal.id} className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {goal.title}
                  </p>
                  <div className="mt-1 flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${goal.progress}%` }}
                      />
                    </div>
                    <span className="ml-2 text-xs text-gray-500">
                      {goal.progress}%
                    </span>
                  </div>
                </div>
                <div className="ml-4 text-sm text-gray-500">
                  {goal.actual_time}/{goal.estimated_time}分钟
                </div>
              </div>
            )) || (
              <p className="text-sm text-gray-500">暂无活跃目标</p>
            )}
          </div>
        </div>

        {/* 最近记录 */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">最近记录</h3>
            <Link
              to="/time-records"
              className="text-sm text-primary-600 hover:text-primary-900"
            >
              查看全部
            </Link>
          </div>
          <div className="space-y-3">
            {todayRecords?.records.slice(0, 5).map((record) => (
              <div key={record.id} className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {record.activity}
                  </p>
                  <p className="text-xs text-gray-500">
                    {format(new Date(record.start_time), 'HH:mm')} - {format(new Date(record.end_time), 'HH:mm')}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                    record.category === '生产' ? 'bg-green-100 text-green-800' :
                    record.category === '投资' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {record.category}
                  </span>
                  <span className="text-sm text-gray-500">
                    {record.duration}分钟
                  </span>
                </div>
              </div>
            )) || (
              <p className="text-sm text-gray-500">今日暂无记录</p>
            )}
          </div>
        </div>
      </div>

      {/* 今日活动分布 */}
      {summaryStats?.top_activities && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">今日活动分布</h3>
          <div className="space-y-3">
            {summaryStats.top_activities.map((activity: any, index: number) => (
              <div key={index} className="flex items-center">
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">
                      {activity.activity}
                    </span>
                    <span className="text-sm text-gray-500">
                      {activity.duration}分钟 ({activity.percentage}%)
                    </span>
                  </div>
                  <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${activity.percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;