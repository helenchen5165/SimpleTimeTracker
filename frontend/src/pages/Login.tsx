// 登录页面
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Smartphone } from 'lucide-react';
import { LoadingButton } from '../components/Loading';
import apiService from '../services/api';
import { toast } from 'react-hot-toast';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  // 开发环境模拟登录
  const handleMockLogin = async () => {
    setIsLoading(true);
    
    try {
      // 模拟微信登录数据
      const mockLoginData = {
        code: `mock_code_${Date.now()}`,
        user_info: {
          nickName: '测试用户',
          avatarUrl: 'https://via.placeholder.com/32x32/3B82F6/FFFFFF?text=U'
        }
      };

      const result = await apiService.login(mockLoginData);
      
      toast.success('登录成功！');
      navigate('/');
    } catch (error: any) {
      toast.error(error.message || '登录失败');
    } finally {
      setIsLoading(false);
    }
  };

  // 真实微信登录（需要在微信环境中）
  const handleWechatLogin = () => {
    toast.info('微信登录功能正在开发中...');
    // TODO: 实现真实的微信登录流程
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Logo和标题 */}
        <div className="flex justify-center">
          <div className="flex items-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-600">
              <Clock className="h-8 w-8 text-white" />
            </div>
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          SimpleTimeTracker
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          智能时间记录与目标管理系统
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="space-y-6">
            {/* 功能介绍 */}
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                开始您的时间管理之旅
              </h3>
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>
                  智能语言解析，轻松记录时间
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>  
                  目标管理，追踪进度完成情况
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>
                  数据可视化，洞察时间分配
                </div>
              </div>
            </div>

            {/* 登录按钮 */}
            <div className="space-y-4">
              {/* 开发环境模拟登录 */}
              {import.meta.env.DEV && (
                <LoadingButton
                  loading={isLoading}
                  onClick={handleMockLogin}
                  className="w-full btn-primary justify-center"
                >
                  <Smartphone className="mr-2 h-5 w-5" />
                  开发环境登录
                </LoadingButton>
              )}

              {/* 微信登录 */}
              <button
                onClick={handleWechatLogin}
                className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.162 4.203 2.969 5.531.54.39.719 1.023.719 1.633v2.11c0 .703.844 1.055 1.367.57l2.109-1.954c.364-.336.84-.492 1.316-.43.528.07 1.056.105 1.592.105 4.799 0 8.691-3.288 8.691-7.342 0-4.054-3.892-7.342-8.691-7.342zm-.3 11.644c-.744 0-1.348-.604-1.348-1.348s.604-1.348 1.348-1.348 1.348.604 1.348 1.348-.604 1.348-1.348 1.348zm5.618 0c-.744 0-1.348-.604-1.348-1.348s.604-1.348 1.348-1.348 1.348.604 1.348 1.348-.604 1.348-1.348 1.348z"/>
                </svg>
                微信登录
              </button>
            </div>

            {/* 隐私说明 */}
            <div className="text-xs text-gray-500 text-center">
              <p>
                登录即表示您同意我们的{' '}
                <a href="#" className="text-primary-600 hover:text-primary-500">
                  服务条款
                </a>{' '}
                和{' '}
                <a href="#" className="text-primary-600 hover:text-primary-500">
                  隐私政策
                </a>
              </p>
            </div>
          </div>
        </div>

        {/* 版本信息 */}
        <div className="mt-8 text-center">
          <p className="text-xs text-gray-400">
            Version 2.1 - Deadline目标管理版
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;