import React, { useState } from 'react';
import { useDailyReport, useWeeklyReport, useSummaryStats } from '../hooks/useApi';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const Reports: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState<'daily' | 'weekly' | 'summary'>('daily');
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );

  const { data: dailyReport, isLoading: dailyLoading, error: dailyError } = useDailyReport(selectedDate);
  const { data: weeklyReport, isLoading: weeklyLoading, error: weeklyError } = useWeeklyReport(selectedDate);
  const { data: summaryStats, isLoading: summaryLoading, error: summaryError } = useSummaryStats();

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}小时${mins}分钟` : `${mins}分钟`;
  };

  const formatPercentage = (percentage: number) => {
    return `${percentage.toFixed(1)}%`;
  };

  const COLORS = {
    '生产': '#10B981', // green-500
    '投资': '#3B82F6', // blue-500
    '支出': '#EF4444'  // red-500
  };

  const RADIAN = Math.PI / 180;
  const renderCustomizedLabel = ({
    cx, cy, midAngle, innerRadius, outerRadius, percent
  }: any) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize="12"
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  const renderDailyReport = () => {
    if (dailyLoading) return <div className="flex justify-center p-8"><div className="spinner"></div></div>;
    if (dailyError) return <div className="text-red-600 p-4">加载日报失败: {dailyError.message}</div>;
    if (!dailyReport) return <div className="text-gray-500 p-4">暂无数据</div>;

    return (
      <div className="space-y-6">
        {/* 概览卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-blue-600">{dailyReport.total_records}</div>
            <div className="text-sm text-gray-600">记录条数</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-green-600">{formatDuration(dailyReport.total_duration)}</div>
            <div className="text-sm text-gray-600">总时长</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-purple-600">{formatPercentage(dailyReport.efficiency_rate)}</div>
            <div className="text-sm text-gray-600">有效率</div>
          </div>
        </div>

        {/* 分类统计 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">分类分布</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={Object.entries(dailyReport.category_stats).map(([category, stats]) => ({
                    name: category,
                    value: stats.duration,
                    percentage: stats.percentage
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={renderCustomizedLabel}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {Object.entries(dailyReport.category_stats).map(([category], index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[category as keyof typeof COLORS] || '#8884d8'} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number) => [formatDuration(value), '时长']}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">分类详情</h3>
            <div className="space-y-3">
              {Object.entries(dailyReport.category_stats).map(([category, stats]) => (
                <div key={category} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div 
                      className="w-3 h-3 rounded-full mr-3"
                      style={{ backgroundColor: COLORS[category as keyof typeof COLORS] || '#8884d8' }}
                    ></div>
                    <span className="font-medium">{category}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold">{formatDuration(stats.duration)}</div>
                    <div className="text-sm text-gray-500">{formatPercentage(stats.percentage)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 活动统计 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">活动统计</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={dailyReport.activity_stats.slice(0, 8).map(activity => ({
                name: activity.activity,
                duration: activity.duration,
                formattedDuration: formatDuration(activity.duration)
              }))}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={80}
                fontSize={12}
              />
              <YAxis 
                tickFormatter={(value) => `${Math.floor(value / 60)}h${value % 60}m`}
              />
              <Tooltip 
                formatter={(value: number) => [formatDuration(value), '时长']}
              />
              <Bar dataKey="duration" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 目标进度 */}
        {dailyReport.goal_progress && dailyReport.goal_progress.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">目标进度</h3>
            <div className="space-y-4">
              {dailyReport.goal_progress.map((goal) => (
                <div key={goal.goal_id} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{goal.title}</span>
                    <span className="text-sm text-gray-600">
                      {formatDuration(goal.progress)} / {formatDuration(goal.estimated)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${Math.min(goal.percentage, 100)}%` }}
                    ></div>
                  </div>
                  <div className="text-right text-sm text-gray-600">
                    {goal.percentage}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderWeeklyReport = () => {
    if (weeklyLoading) return <div className="flex justify-center p-8"><div className="spinner"></div></div>;
    if (weeklyError) return <div className="text-red-600 p-4">加载周报失败: {weeklyError.message}</div>;
    if (!weeklyReport) return <div className="text-gray-500 p-4">暂无数据</div>;

    return (
      <div className="space-y-6">
        {/* 周概览 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">
            {weeklyReport.week} ({weeklyReport.date_range[0]} ~ {weeklyReport.date_range[1]})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-2xl font-bold text-blue-600">{formatDuration(weeklyReport.total_duration)}</div>
              <div className="text-sm text-gray-600">总时长</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{formatPercentage(weeklyReport.efficiency_rate)}</div>
              <div className="text-sm text-gray-600">有效率</div>
            </div>
          </div>
        </div>

        {/* 每日分解 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">每日时长趋势</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={weeklyReport.daily_breakdown.map((day, index) => {
                const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
                return {
                  name: dayNames[index],
                  date: day.breakdown_date,
                  duration: day.duration,
                  formattedDuration: formatDuration(day.duration)
                };
              })}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis 
                tickFormatter={(value) => `${Math.floor(value / 60)}h`}
              />
              <Tooltip 
                formatter={(value: number) => [formatDuration(value), '时长']}
                labelFormatter={(label) => `${label}`}
              />
              <Line 
                type="monotone" 
                dataKey="duration" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* 分类汇总 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">分类汇总</h3>
          <div className="space-y-3">
            {Object.entries(weeklyReport.category_summary).map(([category, stats]) => (
              <div key={category} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-3 ${
                    category === '生产' ? 'bg-green-500' :
                    category === '投资' ? 'bg-blue-500' : 'bg-red-500'
                  }`}></div>
                  <span className="font-medium">{category}</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold">{formatDuration(stats.duration)}</div>
                  <div className="text-sm text-gray-500">{formatPercentage(stats.percentage)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 完成的目标 */}
        {weeklyReport.completed_goals && weeklyReport.completed_goals.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">本周完成的目标</h3>
            <div className="space-y-3">
              {weeklyReport.completed_goals.map((goal, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="font-medium text-green-800">{goal.title}</span>
                  <div className="text-right text-sm text-green-600">
                    <div>预估: {formatDuration(goal.estimated_time)}</div>
                    <div>实际: {formatDuration(goal.actual_time)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderSummaryStats = () => {
    if (summaryLoading) return <div className="flex justify-center p-8"><div className="spinner"></div></div>;
    if (summaryError) return <div className="text-red-600 p-4">加载概览失败: {summaryError.message}</div>;
    if (!summaryStats) return <div className="text-gray-500 p-4">暂无数据</div>;

    return (
      <div className="space-y-6">
        {/* 快速概览 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-blue-600">{formatDuration(summaryStats.today_duration)}</div>
            <div className="text-sm text-gray-600">今日时长</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-green-600">{formatDuration(summaryStats.week_duration)}</div>
            <div className="text-sm text-gray-600">本周时长</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-purple-600">{summaryStats.active_goals}</div>
            <div className="text-sm text-gray-600">活跃目标</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-orange-600">{formatPercentage(summaryStats.avg_daily_efficiency)}</div>
            <div className="text-sm text-gray-600">平均有效率</div>
          </div>
        </div>

        {/* 热门活动 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">热门活动</h3>
          <div className="space-y-3">
            {summaryStats.top_activities?.map((activity: any, index: number) => (
              <div key={activity.activity} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold mr-3">
                    {index + 1}
                  </div>
                  <span className="font-medium">{activity.activity}</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold">{formatDuration(activity.duration)}</div>
                  <div className="text-sm text-gray-500">{formatPercentage(activity.percentage)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 最近成就 */}
        {summaryStats.recent_achievements && summaryStats.recent_achievements.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">最近成就</h3>
            <div className="space-y-3">
              {summaryStats.recent_achievements.map((achievement: any, index: number) => (
                <div key={index} className="flex items-center p-3 bg-yellow-50 rounded-lg">
                  <div className="w-8 h-8 bg-yellow-100 text-yellow-600 rounded-full flex items-center justify-center mr-3">
                    🏆
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-yellow-800">{achievement.title}</div>
                    <div className="text-sm text-yellow-600">{achievement.date}</div>
                  </div>
                  <div className="text-xs bg-yellow-200 text-yellow-700 px-2 py-1 rounded">
                    {achievement.type === 'goal_completed' ? '目标完成' : '连续记录'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">数据报告</h1>
        <p className="text-gray-600">查看您的时间统计和分析报告</p>
      </div>

      {/* 日期选择器 */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          选择日期
        </label>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* 标签页 */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'daily', label: '日报' },
            { key: 'weekly', label: '周报' },
            { key: 'summary', label: '概览' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setSelectedTab(tab.key as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                selectedTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* 报告内容 */}
      <div>
        {selectedTab === 'daily' && renderDailyReport()}
        {selectedTab === 'weekly' && renderWeeklyReport()}
        {selectedTab === 'summary' && renderSummaryStats()}
      </div>
    </div>
  );
};

export default Reports;