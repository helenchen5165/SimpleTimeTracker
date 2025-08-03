"""
用户认证API路由
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from datetime import timedelta
import httpx
import logging

from api.models.schemas import (
    WechatLoginRequest, LoginResponse, TokenRefreshResponse,
    ApiResponse, UserInfo
)
from api.middleware.auth import JWTManager, get_current_user
from api.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
jwt_manager = JWTManager()

@router.post("/wechat/login", response_model=ApiResponse)
async def wechat_login(login_data: WechatLoginRequest):
    """微信登录"""
    settings = get_settings()
    
    try:
        # 向微信服务器验证code
        wechat_response = await _verify_wechat_code(
            login_data.code,
            settings.wechat_app_id,
            settings.wechat_app_secret
        )
        
        if not wechat_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="微信授权验证失败"
            )
        
        openid = wechat_response.get("openid")
        if not openid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="获取微信用户信息失败"
            )
        
        # 创建或获取用户信息
        user = await _create_or_get_user(openid, login_data.user_info)
        
        # 生成JWT Token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = jwt_manager.create_access_token(
            data={"sub": user.id, "openid": openid},
            expires_delta=access_token_expires
        )
        
        response_data = LoginResponse(
            token=access_token,
            user=user
        )
        
        return ApiResponse(
            success=True,
            data=response_data.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"微信登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录服务异常"
        )

@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(request: Request, current_user: dict = Depends(get_current_user)):
    """刷新Token"""
    try:
        settings = get_settings()
        
        # 生成新的访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        new_token = jwt_manager.create_access_token(
            data={"sub": current_user.get("sub"), "openid": current_user.get("openid")},
            expires_delta=access_token_expires
        )
        
        response_data = TokenRefreshResponse(token=new_token)
        
        return ApiResponse(
            success=True,
            data=response_data.dict()
        )
        
    except Exception as e:
        logger.error(f"刷新Token失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token刷新失败"
        )

@router.get("/me", response_model=ApiResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    try:
        # TODO: 从数据库查询完整用户信息
        user_info = UserInfo(
            id=current_user.get("sub", ""),
            nickname="测试用户",
            avatar="https://example.com/avatar.jpg",
            created_at="2025-07-28T10:00:00Z"
        )
        
        return ApiResponse(
            success=True,
            data=user_info.dict()
        )
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )

# =============== 私有辅助函数 ===============

async def _verify_wechat_code(code: str, app_id: str, app_secret: str) -> dict:
    """验证微信授权码"""
    if not app_id or not app_secret:
        logger.warning("微信配置未设置，使用模拟模式")
        # 开发模式下返回模拟数据
        return {
            "openid": f"mock_openid_{code}",
            "session_key": "mock_session_key"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.weixin.qq.com/sns/jscode2session",
                params={
                    "appid": app_id,
                    "secret": app_secret,
                    "js_code": code,
                    "grant_type": "authorization_code"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if "errcode" in data:
                    logger.error(f"微信API错误: {data}")
                    return None
                return data
            else:
                logger.error(f"微信API请求失败: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"微信API请求异常: {e}")
        return None

async def _create_or_get_user(openid: str, user_info: dict) -> UserInfo:
    """创建或获取用户"""
    # TODO: 实际的用户数据库操作
    # 这里暂时返回模拟数据
    
    user = UserInfo(
        id=f"user_{openid}",
        nickname=user_info.get("nickName", "匿名用户"),
        avatar=user_info.get("avatarUrl", ""),
        created_at="2025-07-28T10:00:00Z"
    )
    
    logger.info(f"用户登录: {user.nickname} ({user.id})")
    return user