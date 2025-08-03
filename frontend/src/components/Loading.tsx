// 加载组件
import React from 'react';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const Loading: React.FC<LoadingProps> = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div className={`loading-spinner ${sizeClasses[size]}`}></div>
    </div>
  );
};

// 页面级加载组件
export const PageLoading: React.FC = () => {
  return (
    <div className="flex min-h-[400px] items-center justify-center">
      <div className="text-center">
        <Loading size="lg" />
        <p className="mt-4 text-sm text-gray-500">加载中...</p>
      </div>
    </div>
  );
};

// 按钮加载状态
interface LoadingButtonProps {
  loading: boolean;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit';
}

export const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading,
  children,
  className = '',
  onClick,
  disabled,
  type = 'button'
}) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`btn flex items-center justify-center ${className} ${
        loading ? 'opacity-75 cursor-not-allowed' : ''
      }`}
    >
      {loading && <Loading size="sm" className="mr-2" />}
      {children}
    </button>
  );
};

export default Loading;