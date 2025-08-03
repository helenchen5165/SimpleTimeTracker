"""
应用配置管理
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os
from functools import lru_cache

class Settings(BaseSettings):
    """应用设置"""
    
    # 基础配置
    debug: bool = Field(default=False, description="调试模式")
    host: str = Field(default="0.0.0.0", description="服务器地址")
    port: int = Field(default=8000, description="服务器端口")
    
    # 安全配置
    secret_key: str = Field(..., description="JWT密钥")
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="Token过期时间(分钟)")
    
    # CORS配置
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://localhost:5174"],
        description="允许的前端域名"
    )
    
    # Notion API配置
    notion_token: str = Field(..., description="Notion API Token")
    database_id: str = Field(..., description="时间记录数据库ID")
    goals_database_id: str = Field(..., description="目标数据库ID")
    page_id: str = Field(default="", description="周报页面ID")
    
    # Claude API配置
    anthropic_api_key: str = Field(default="", description="Claude API密钥")
    claude_model: str = Field(default="claude-3-5-sonnet-20241022", description="Claude模型")
    claude_max_tokens: int = Field(default=1000, description="Claude最大令牌数")
    claude_temperature: float = Field(default=0.1, description="Claude温度参数")
    
    # 系统配置
    timezone: str = Field(default="Asia/Shanghai", description="时区")
    log_level: str = Field(default="INFO", description="日志级别")
    
    # 活动分类配置
    production_activities: str = Field(
        default="沟通,管理,输出,总结,目标,吉他,家庭,助人,分享,商业,写作,组织,执行,创新,编程",
        description="生产类活动"
    )
    investment_activities: str = Field(
        default="健康,旅行,人脉,交易,运动,冥想,阅读,恋爱,学习,朋友,播客",
        description="投资类活动"
    )
    expense_activities: str = Field(
        default="购物,日常,睡觉,情绪,无意识,通勤,视频,社交,耍手机,吃饭,杂事,游戏,看电视,休息",
        description="支出类活动"
    )
    
    # 微信配置
    wechat_app_id: str = Field(default="", description="微信AppID")
    wechat_app_secret: str = Field(default="", description="微信AppSecret")
    
    # 报告配置
    daily_report_time: str = Field(default="22:59", description="日报时间")
    weekly_report_day: str = Field(default="Sunday", description="周报日期")
    weekly_report_time: str = Field(default="21:00", description="周报时间")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": 'utf-8',
        "case_sensitive": False,
        "extra": "ignore"
    }

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()