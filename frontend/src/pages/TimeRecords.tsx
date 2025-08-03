// 时间记录页面
import React, { useState } from 'react';
import { Plus, Calendar, Clock, Edit, Trash2, X } from 'lucide-react';
import { PageLoading, LoadingButton } from '../components/Loading';
import { useTimeRecords, useCreateTimeRecord, useUpdateTimeRecord, useDeleteTimeRecord } from '../hooks/useApi';
import { format, parseISO } from 'date-fns';
import type { TimeRecord } from '../types/api';

const TimeRecords: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [isAddingRecord, setIsAddingRecord] = useState(false);
  const [inputText, setInputText] = useState('');
  const [editingRecord, setEditingRecord] = useState<TimeRecord | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const { data: recordsData, isLoading, refetch } = useTimeRecords({
    target_date: selectedDate,
    limit: 50
  });

  const createTimeRecord = useCreateTimeRecord();
  const updateTimeRecord = useUpdateTimeRecord();
  const deleteTimeRecord = useDeleteTimeRecord();

  const handleAddRecord = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    try {
      await createTimeRecord.mutateAsync({
        input_text: inputText.trim()
      });
      setInputText('');
      setIsAddingRecord(false);
      refetch();
    } catch (error) {
      // Error is handled by the hook
    }
  };

  const handleEditRecord = (record: TimeRecord) => {
    setEditingRecord(record);
    setIsAddingRecord(false);
  };

  const handleUpdateRecord = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingRecord) return;

    try {
      const formData = new FormData(e.target as HTMLFormElement);
      const startTime = formData.get('start_time') as string;
      const endTime = formData.get('end_time') as string;
      const activity = formData.get('activity') as string;

      await updateTimeRecord.mutateAsync({
        recordId: editingRecord.id,
        recordData: {
          start_time: startTime ? new Date(startTime) : undefined,
          end_time: endTime ? new Date(endTime) : undefined,
          activity: activity || undefined
        }
      });
      
      setEditingRecord(null);
      refetch();
    } catch (error) {
      // Error is handled by the hook
    }
  };

  const handleDeleteRecord = async (recordId: string) => {
    try {
      await deleteTimeRecord.mutateAsync(recordId);
      setDeleteConfirmId(null);
      refetch();
    } catch (error) {
      // Error is handled by the hook
    }
  };

  const cancelEdit = () => {
    setEditingRecord(null);
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
            时间记录
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            管理和查看您的时间记录
          </p>
        </div>
        <div className="mt-4 flex space-x-3 md:ml-4 md:mt-0">
          <button
            onClick={() => {
              setIsAddingRecord(true);
              setEditingRecord(null);
            }}
            className="btn btn-primary inline-flex items-center"
          >
            <Plus className="mr-2 h-4 w-4" />
            添加记录
          </button>
        </div>
      </div>

      {/* 日期选择和筛选 */}
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Calendar className="h-5 w-5 text-gray-400" />
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="input text-sm"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Clock className="h-4 w-4" />
            <span>
              共 {recordsData?.total || 0} 条记录，
              总时长 {recordsData?.total_duration || 0} 分钟
            </span>
          </div>
        </div>
      </div>

      {/* 添加记录表单 */}
      {isAddingRecord && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">添加时间记录</h3>
          <form onSubmit={handleAddRecord} className="space-y-4">
            <div>
              <label htmlFor="input-text" className="block text-sm font-medium text-gray-700">
                时间描述
              </label>
              <input
                type="text"
                id="input-text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="例如：9点到11点学习Python编程"
                className="input mt-1"
                autoFocus
              />
              <p className="mt-1 text-xs text-gray-500">
                支持自然语言描述，系统会智能解析时间和活动内容
              </p>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setIsAddingRecord(false);
                  setInputText('');
                }}
                className="btn btn-secondary"
              >
                取消
              </button>
              <LoadingButton
                type="submit"
                loading={createTimeRecord.isPending}
                className="btn-primary"
              >
                添加记录
              </LoadingButton>
            </div>
          </form>
        </div>
      )}

      {/* 编辑记录表单 */}
      {editingRecord && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">编辑时间记录</h3>
          <form onSubmit={handleUpdateRecord} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="edit-start-time" className="block text-sm font-medium text-gray-700">
                  开始时间
                </label>
                <input
                  type="datetime-local"
                  id="edit-start-time"
                  name="start_time"
                  defaultValue={editingRecord.start_time ? format(parseISO(editingRecord.start_time), "yyyy-MM-dd'T'HH:mm") : ''}
                  className="input mt-1"
                />
              </div>
              <div>
                <label htmlFor="edit-end-time" className="block text-sm font-medium text-gray-700">
                  结束时间
                </label>
                <input
                  type="datetime-local"
                  id="edit-end-time"
                  name="end_time"
                  defaultValue={editingRecord.end_time ? format(parseISO(editingRecord.end_time), "yyyy-MM-dd'T'HH:mm") : ''}
                  className="input mt-1"
                />
              </div>
            </div>
            <div>
              <label htmlFor="edit-activity" className="block text-sm font-medium text-gray-700">
                活动类型
              </label>
              <input
                type="text"
                id="edit-activity"
                name="activity"
                defaultValue={editingRecord.activity}
                className="input mt-1"
                placeholder="例如：编程、学习、运动等"
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={cancelEdit}
                className="btn btn-secondary"
              >
                取消
              </button>
              <LoadingButton
                type="submit"
                loading={updateTimeRecord.isPending}
                className="btn-primary"
              >
                保存更改
              </LoadingButton>
            </div>
          </form>
        </div>
      )}

      {/* 记录列表 */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {format(parseISO(selectedDate), 'yyyy年MM月dd日')} 的记录
        </h3>
        
        {recordsData?.records && recordsData.records.length > 0 ? (
          <div className="space-y-4">
            {recordsData.records.map((record) => (
              <div
                key={record.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h4 className="text-sm font-medium text-gray-900">
                      {record.activity}
                    </h4>
                    <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                      record.category === '生产' ? 'bg-green-100 text-green-800' :
                      record.category === '投资' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {record.category}
                    </span>
                    {record.parsing_method === 'Claude' && (
                      <span className="inline-flex items-center rounded-full bg-purple-100 px-2 py-1 text-xs font-medium text-purple-800">
                        🤖 AI解析
                      </span>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-gray-600">
                    {record.description}
                  </p>
                  <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                    <span>
                      {format(parseISO(record.start_time), 'HH:mm')} - {format(parseISO(record.end_time), 'HH:mm')}
                    </span>
                    <span>时长: {record.duration}分钟</span>
                    {record.confidence && (
                      <span>置信度: {record.confidence}%</span>
                    )}
                  </div>
                  {record.matched_goal && (
                    <div className="mt-2">
                      <span className="inline-flex items-center rounded-full bg-primary-100 px-2 py-1 text-xs font-medium text-primary-800">
                        🎯 {record.matched_goal.title}
                      </span>
                    </div>
                  )}
                </div>
                
                {/* 操作按钮 */}
                <div className="flex items-center space-x-2">
                  {deleteConfirmId === record.id ? (
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">确定删除？</span>
                      <button
                        onClick={() => handleDeleteRecord(record.id)}
                        className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                        disabled={deleteTimeRecord.isPending}
                      >
                        {deleteTimeRecord.isPending ? '删除中...' : '确定'}
                      </button>
                      <button
                        onClick={() => setDeleteConfirmId(null)}
                        className="px-2 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                      >
                        取消
                      </button>
                    </div>
                  ) : (
                    <>
                      <button
                        onClick={() => handleEditRecord(record)}
                        className="flex items-center space-x-1 text-primary-600 hover:text-primary-900 text-sm"
                        disabled={editingRecord !== null}
                      >
                        <Edit className="h-4 w-4" />
                        <span>编辑</span>
                      </button>
                      <button
                        onClick={() => setDeleteConfirmId(record.id)}
                        className="flex items-center space-x-1 text-red-600 hover:text-red-900 text-sm"
                      >
                        <Trash2 className="h-4 w-4" />
                        <span>删除</span>
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Clock className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">暂无时间记录</h3>
            <p className="mt-1 text-sm text-gray-500">
              开始添加您的第一条时间记录
            </p>
            <div className="mt-6">
              <button
                onClick={() => {
                  setIsAddingRecord(true);
                  setEditingRecord(null);
                }}
                className="btn btn-primary inline-flex items-center"
              >
                <Plus className="mr-2 h-4 w-4" />
                添加记录
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TimeRecords;