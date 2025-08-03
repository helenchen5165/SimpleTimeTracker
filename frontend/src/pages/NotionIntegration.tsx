import React, { useState, useEffect } from 'react';
import { ExternalLink, Database, FileText, CheckCircle, AlertCircle, Copy, Eye, EyeOff } from 'lucide-react';
import apiService from '../services/api';
import type { NotionDatabase, NotionPage, NotionSetupStep } from '../types/api';

const NotionIntegration: React.FC = () => {
  const [step, setStep] = useState<'guide' | 'connect' | 'select'>('guide');
  const [token, setToken] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [setupGuide, setSetupGuide] = useState<{ title: string; steps: NotionSetupStep[] } | null>(null);
  const [databases, setDatabases] = useState<NotionDatabase[]>([]);
  const [selectedDatabase, setSelectedDatabase] = useState<NotionDatabase | null>(null);
  const [pages, setPages] = useState<NotionPage[]>([]);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  useEffect(() => {
    loadSetupGuide();
  }, []);

  const loadSetupGuide = async () => {
    try {
      const response = await apiService.getNotionSetupGuide();
      setSetupGuide(response.guide);
    } catch (error: any) {
      console.error('Failed to load setup guide:', error);
    }
  };

  const handleConnectNotion = async () => {
    if (!token.trim()) {
      setError('请输入 Notion Integration Token');
      return;
    }

    if (!token.startsWith('secret_')) {
      setError('Token 格式不正确，应该以 "secret_" 开头');
      return;
    }

    setIsConnecting(true);
    setError('');

    try {
      const response = await apiService.connectNotion(token);
      setSuccess(`✅ ${response.message}！找到 ${response.databases_count} 个数据库`);
      
      // 获取完整的数据库列表
      const dbResponse = await apiService.getNotionDatabases(token);
      setDatabases(dbResponse.databases);
      setStep('select');
    } catch (error: any) {
      setError(error.message || 'Notion 连接失败');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleSelectDatabase = async (database: NotionDatabase) => {
    setSelectedDatabase(database);
    setIsLoading(true);
    setError('');

    try {
      const response = await apiService.getNotionPages(database.id, token);
      setPages(response.pages);
      setSuccess(`✅ 已选择数据库 "${database.title}"，找到 ${response.total} 个页面`);
    } catch (error: any) {
      setError(`获取数据库页面失败: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setSuccess('已复制到剪贴板');
    setTimeout(() => setSuccess(''), 2000);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (step === 'guide') {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">连接 Notion 数据库</h1>
          <p className="text-gray-600">
            将您的 Notion 数据库与 SimpleTimeTracker 连接，实现数据同步和管理
          </p>
        </div>

        {/* 设置指南 */}
        {setupGuide && (
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">{setupGuide.title}</h2>
            <div className="space-y-4">
              {setupGuide.steps.map((stepItem) => (
                <div key={stepItem.step} className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
                    {stepItem.step}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 mb-1">{stepItem.title}</h3>
                    <p className="text-sm text-gray-600 mb-2">{stepItem.description}</p>
                    <p className="text-sm font-medium text-primary-600">{stepItem.action}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 快速链接 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center mb-2">
            <ExternalLink className="h-5 w-5 text-blue-600 mr-2" />
            <h3 className="font-medium text-blue-900">快速链接</h3>
          </div>
          <div className="space-y-2">
            <a
              href="https://www.notion.so/my-integrations"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
            >
              <ExternalLink className="h-4 w-4 mr-1" />
              Notion Integrations 页面
            </a>
            <br />
            <a
              href="https://developers.notion.com/docs/getting-started"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
            >
              <ExternalLink className="h-4 w-4 mr-1" />
              Notion API 文档
            </a>
          </div>
        </div>

        <div className="flex justify-center">
          <button
            onClick={() => setStep('connect')}
            className="btn btn-primary px-8 py-3 text-lg"
          >
            我已准备好 Integration Token
          </button>
        </div>
      </div>
    );
  }

  if (step === 'connect') {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">连接 Notion</h1>
          <p className="text-gray-600">
            请输入您的 Notion Integration Token 来连接数据库
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="mb-4">
            <label htmlFor="token" className="block text-sm font-medium text-gray-700 mb-2">
              Notion Integration Token
            </label>
            <div className="relative">
              <input
                type={showToken ? "text" : "password"}
                id="token"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="secret_..."
                className="input pr-20"
                disabled={isConnecting}
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 space-x-2">
                <button
                  type="button"
                  onClick={() => setShowToken(!showToken)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  {showToken ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Token 应该以 "secret_" 开头，可以在 Notion Integrations 页面找到
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-center">
                <AlertCircle className="h-4 w-4 text-red-600 mr-2" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                <span className="text-sm text-green-700">{success}</span>
              </div>
            </div>
          )}

          <div className="flex space-x-3">
            <button
              onClick={() => setStep('guide')}
              className="btn btn-secondary flex-1"
              disabled={isConnecting}
            >
              返回指南
            </button>
            <button
              onClick={handleConnectNotion}
              disabled={isConnecting || !token.trim()}
              className="btn btn-primary flex-1"
            >
              {isConnecting ? '连接中...' : '连接 Notion'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">选择 Notion 数据库</h1>
        <p className="text-gray-600">
          从您的 Notion 工作区中选择要集成的数据库
        </p>
      </div>

      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-sm text-green-700">{success}</span>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
            <span className="text-sm text-red-700">{error}</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 数据库列表 */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Database className="h-5 w-5 mr-2" />
            可用数据库 ({databases.length})
          </h2>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {databases.map((database) => (
              <div
                key={database.id}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedDatabase?.id === database.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
                onClick={() => handleSelectDatabase(database)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 mb-1">{database.title}</h3>
                    <p className="text-xs text-gray-500">
                      创建: {formatDate(database.created_time)}
                    </p>
                    <p className="text-xs text-gray-500">
                      更新: {formatDate(database.last_edited_time)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(database.id);
                      }}
                      className="text-gray-400 hover:text-gray-600"
                      title="复制 ID"
                    >
                      <Copy className="h-4 w-4" />
                    </button>
                    <a
                      href={database.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="text-gray-400 hover:text-gray-600"
                      title="在 Notion 中打开"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                </div>

                {/* 属性预览 */}
                <div className="mt-2 flex flex-wrap gap-1">
                  {Object.values(database.properties).slice(0, 4).map((prop, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-gray-100 text-xs text-gray-600 rounded"
                    >
                      {prop.name} ({prop.type})
                    </span>
                  ))}
                  {Object.keys(database.properties).length > 4 && (
                    <span className="px-2 py-1 bg-gray-100 text-xs text-gray-600 rounded">
                      +{Object.keys(database.properties).length - 4} 更多
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 页面列表 */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            数据库页面 ({pages.length})
          </h2>

          {selectedDatabase ? (
            <div>
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-sm text-blue-700">
                  <strong>已选择:</strong> {selectedDatabase.title}
                </p>
              </div>

              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="text-center">
                    <div className="loading-spinner mx-auto mb-2"></div>
                    <p className="text-sm text-gray-500">加载页面中...</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {pages.map((page) => (
                    <div
                      key={page.id}
                      className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 mb-1">{page.title}</h4>
                          <p className="text-xs text-gray-500">
                            更新: {formatDate(page.last_edited_time)}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => copyToClipboard(page.id)}
                            className="text-gray-400 hover:text-gray-600"
                            title="复制 ID"
                          >
                            <Copy className="h-4 w-4" />
                          </button>
                          <a
                            href={page.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-400 hover:text-gray-600"
                            title="在 Notion 中打开"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center py-8 text-gray-500">
              <div className="text-center">
                <Database className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p>请先选择一个数据库</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="mt-8 flex justify-between">
        <button
          onClick={() => setStep('connect')}
          className="btn btn-secondary"
        >
          重新连接
        </button>
        
        {selectedDatabase && (
          <button
            onClick={() => {
              // TODO: 保存选择的数据库配置
              alert(`已选择数据库: ${selectedDatabase.title}\n包含 ${pages.length} 个页面`);
            }}
            className="btn btn-primary"
          >
            确认选择此数据库
          </button>
        )}
      </div>
    </div>
  );
};

export default NotionIntegration;