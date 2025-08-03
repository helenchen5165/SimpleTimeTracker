import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, Target, Clock, BarChart3 } from 'lucide-react';

const SimpleDashboard: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 简单的头部 */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600">
                <Clock className="h-5 w-5 text-white" />
              </div>
              <span className="ml-3 text-lg font-semibold text-gray-900">
                SimpleTimeTracker
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
            >
              <LogOut className="mr-2 h-4 w-4" />
              退出登录
            </button>
          </div>
        </div>
      </div>

      {/* 主内容 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">欢迎回来！</h1>
          <p className="mt-1 text-sm text-gray-500">这是您的时间管理概览</p>
        </div>

        {/* 功能卡片 */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {/* 时间记录卡片 */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Clock className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <h3 className="text-lg font-medium text-gray-900">时间记录</h3>
                  <p className="mt-1 text-sm text-gray-500">记录和管理您的时间</p>
                </div>
              </div>
              <div className="mt-4">
                <button className="btn btn-primary">
                  开始记录
                </button>
              </div>
            </div>
          </div>

          {/* 目标管理卡片 */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Target className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <h3 className="text-lg font-medium text-gray-900">目标管理</h3>
                  <p className="mt-1 text-sm text-gray-500">设定和追踪您的目标</p>
                </div>
              </div>
              <div className="mt-4">
                <button className="btn btn-secondary">
                  管理目标
                </button>
              </div>
            </div>
          </div>

          {/* 数据报告卡片 */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart3 className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <h3 className="text-lg font-medium text-gray-900">数据报告</h3>
                  <p className="mt-1 text-sm text-gray-500">查看您的时间统计</p>
                </div>
              </div>
              <div className="mt-4">
                <button className="btn btn-secondary">
                  查看报告
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 快速统计 */}
        <div className="mt-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">今日概览</h2>
          <div className="bg-white shadow rounded-lg p-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="text-center">
                <div className="text-2xl font-semibold text-primary-600">0</div>
                <div className="text-sm text-gray-500">今日记录</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-semibold text-green-600">0</div>
                <div className="text-sm text-gray-500">活跃目标</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-semibold text-blue-600">0分钟</div>
                <div className="text-sm text-gray-500">今日时长</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleDashboard;