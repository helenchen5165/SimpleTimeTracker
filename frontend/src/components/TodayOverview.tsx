import React from 'react';
import { useTodayOverview } from '../hooks/useApi';
import { Clock, Target, TrendingUp, Activity, RefreshCw } from 'lucide-react';

const TodayOverview: React.FC = () => {
  const { data: overview, isLoading, error, refetch, isRefetching } = useTodayOverview();

  const formatDuration = (minutes: number) => {
    if (minutes === 0) return '0分钟';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}小时${mins}分钟` : `${mins}分钟`;
  };

  if (isLoading) {
    return (
      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">今日概览</h2>
        <div className="bg-white shadow rounded-lg p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="text-center">
                <div className="w-8 h-8 bg-gray-200 rounded mx-auto mb-2 animate-pulse"></div>
                <div className="w-16 h-4 bg-gray-200 rounded mx-auto animate-pulse"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">今日概览</h2>
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-center text-red-600">
            <p>加载失败，请稍后重试</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-medium text-gray-900">今日概览</h2>
        <button
          onClick={() => refetch()}
          disabled={isRefetching}
          className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 mr-1 ${isRefetching ? 'animate-spin' : ''}`} />
          刷新
        </button>
      </div>
      <div className="bg-white shadow rounded-lg p-6">
        {/* 基础统计 */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 mb-6">
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Clock className="h-5 w-5 text-primary-600 mr-1" />
              <div className="text-2xl font-semibold text-primary-600">
                {overview?.today_records || 0}
              </div>
            </div>
            <div className="text-sm text-gray-500">今日记录</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Target className="h-5 w-5 text-green-600 mr-1" />
              <div className="text-2xl font-semibold text-green-600">
                {overview?.active_goals || 0}
              </div>
            </div>
            <div className="text-sm text-gray-500">活跃目标</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <TrendingUp className="h-5 w-5 text-blue-600 mr-1" />
              <div className="text-2xl font-semibold text-blue-600">
                {formatDuration(overview?.today_duration || 0)}
              </div>
            </div>
            <div className="text-sm text-gray-500">今日时长</div>
          </div>
        </div>

        {/* 效率指标 */}
        {overview?.efficiency_rate !== undefined && (
          <div className="border-t pt-4 mb-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">今日效率</span>
              <span className="text-sm font-semibold text-purple-600">
                {overview.efficiency_rate}%
              </span>
            </div>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-600 h-2 rounded-full transition-all"
                style={{ width: `${Math.min(overview.efficiency_rate, 100)}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* 分类分布 */}
        {overview?.category_breakdown && Object.keys(overview.category_breakdown).length > 0 && (
          <div className="border-t pt-4 mb-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">分类分布</h3>
            <div className="space-y-2">
              {Object.entries(overview.category_breakdown).map(([category, duration]) => (
                <div key={category} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div 
                      className={`w-3 h-3 rounded-full mr-2 ${
                        category === '生产' ? 'bg-green-500' :
                        category === '投资' ? 'bg-blue-500' : 'bg-red-500'
                      }`}
                    ></div>
                    <span className="text-sm text-gray-600">{category}</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {formatDuration(duration as number)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 热门活动 */}
        {overview?.top_activities && overview.top_activities.length > 0 && (
          <div className="border-t pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">热门活动</h3>
            <div className="space-y-2">
              {overview.top_activities.slice(0, 3).map((activity: any, index: number) => (
                <div key={activity.activity} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-5 h-5 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold mr-2">
                      {index + 1}
                    </div>
                    <span className="text-sm text-gray-600">{activity.activity}</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {formatDuration(activity.duration)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 最近活动 */}
        {overview?.recent_records && overview.recent_records.length > 0 && (
          <div className="border-t pt-4 mt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">最近活动</h3>
            <div className="space-y-2">
              {overview.recent_records.slice(0, 3).map((record: any) => (
                <div key={record.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div className="flex items-center">
                    <Activity className="h-4 w-4 text-gray-400 mr-2" />
                    <div>
                      <span className="text-sm font-medium text-gray-900">{record.activity}</span>
                      <div className="text-xs text-gray-500 truncate max-w-48">
                        {record.description}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-medium text-gray-700">
                      {formatDuration(record.duration)}
                    </span>
                    <div className="text-xs text-gray-500">
                      {new Date(record.start_time).toLocaleTimeString('zh-CN', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 无数据状态 */}
        {overview && overview.today_records === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Clock className="mx-auto h-12 w-12 text-gray-400 mb-3" />
            <p className="text-base font-medium text-gray-900 mb-1">今天还没有时间记录</p>
            <p className="text-sm text-gray-500 mb-4">开始记录您的第一个活动吧！</p>
            <div className="flex flex-col sm:flex-row gap-2 justify-center">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                💡 试试说："9点到11点学习编程"
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TodayOverview;