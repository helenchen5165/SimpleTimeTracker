"""
JWT认证中间件
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import logging

from api.config.settings import get_settings

logger = logging.getLogger(__name__)

class JWTMiddleware(BaseHTTPMiddleware):
    """JWT认证中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        
        # 不需要认证的路径
        self.public_paths = {
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/v1/auth/wechat/login"
        }
    
    async def dispatch(self, request: Request, call_next):
        """中间件处理逻辑"""
        
        # 跳过OPTIONS预检请求
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # 检查是否为公开路径
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # 检查是否为静态文件
        if request.url.path.startswith("/static/"):
            return await call_next(request)
        
        # 提取并验证JWT Token
        try:
            token = self._extract_token(request)
            if not token:
                return self._unauthorized_response("Missing authentication token")
            
            payload = self._verify_token(token)
            if not payload:
                return self._unauthorized_response("Invalid authentication token")
            
            # 将用户信息添加到请求状态
            request.state.user_id = payload.get("sub")
            request.state.user_data = payload
            
        except HTTPException as e:
            return self._unauthorized_response(str(e.detail))
        except Exception as e:
            logger.error(f"认证中间件错误: {e}")
            return self._server_error_response("Authentication error")
        
        return await call_next(request)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """从请求中提取JWT Token"""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None
    
    def _verify_token(self, token: str) -> Optional[dict]:
        """验证JWT Token"""
        # 开发环境：允许模拟token
        if self.settings.debug and token.startswith("mock_token_"):
            return {
                "sub": "mock_user",
                "nickname": "测试用户",
                "exp": datetime.utcnow().timestamp() + 3600  # 1小时后过期
            }
        
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm]
            )
            
            # 检查过期时间
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                return None
            
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT验证失败: {e}")
            return None
    
    def _unauthorized_response(self, message: str) -> JSONResponse:
        """返回未授权响应"""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "error": {
                    "code": "AUTH_REQUIRED",
                    "message": message
                }
            }
        )
    
    def _server_error_response(self, message: str) -> JSONResponse:
        """返回服务器错误响应"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "SERVER_ERROR",
                    "message": message
                }
            }
        )

# JWT工具函数
class JWTManager:
    """JWT管理器"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.secret_key,
            algorithm=self.settings.algorithm
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """验证令牌"""
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm]
            )
            return payload
        except JWTError:
            return None

# 获取当前用户的依赖注入函数
def get_current_user(request: Request) -> dict:
    """获取当前用户信息"""
    if not hasattr(request.state, 'user_data'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return request.state.user_data