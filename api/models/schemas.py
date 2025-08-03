"""
API数据模型定义
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from datetime import date as DateType
from enum import Enum

# =============== 枚举类型 ===============

class PriorityEnum(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class StatusEnum(str, Enum):
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ABANDONED = "Abandoned"

class CategoryEnum(str, Enum):
    PRODUCTION = "生产"
    INVESTMENT = "投资"
    EXPENSE = "支出"

class ParsingMethodEnum(str, Enum):
    CLAUDE = "Claude"
    RULES = "Rules"

# =============== 基础响应模型 ===============

class ErrorDetail(BaseModel):
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    details: Optional[Any] = Field(None, description="错误详情")

class ApiResponse(BaseModel):
    success: bool = Field(..., description="请求是否成功")
    data: Optional[Any] = Field(None, description="响应数据")
    error: Optional[ErrorDetail] = Field(None, description="错误信息")
    meta: Optional[Dict[str, Any]] = Field(None, description="元数据")

# =============== 用户认证模型 ===============

class WechatLoginRequest(BaseModel):
    code: str = Field(..., description="微信授权码")
    user_info: Dict[str, Any] = Field(..., description="用户信息")

class UserInfo(BaseModel):
    id: str = Field(..., description="用户ID")
    nickname: str = Field(..., description="用户昵称")
    avatar: str = Field(..., description="头像URL")
    created_at: datetime = Field(..., description="创建时间")

class LoginResponse(BaseModel):
    token: str = Field(..., description="JWT Token")
    user: UserInfo = Field(..., description="用户信息")

class TokenRefreshResponse(BaseModel):
    token: str = Field(..., description="新的JWT Token")

# =============== 目标管理模型 ===============

class GoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="目标标题")
    deadline: DateType = Field(..., description="截止日期")
    estimated_time: int = Field(..., ge=0, description="预估时长(分钟)")
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM, description="优先级")

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="目标标题")
    deadline: Optional[DateType] = Field(None, description="截止日期")
    estimated_time: Optional[int] = Field(None, ge=0, description="预估时长(分钟)")
    priority: Optional[PriorityEnum] = Field(None, description="优先级")
    status: Optional[StatusEnum] = Field(None, description="状态")

class Goal(GoalBase):
    id: str = Field(..., description="目标ID")
    actual_time: int = Field(default=0, description="实际投入时长(分钟)")
    progress: int = Field(default=0, ge=0, le=100, description="完成进度(0-100)")
    status: StatusEnum = Field(default=StatusEnum.PLANNED, description="状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class GoalListResponse(BaseModel):
    goals: List[Goal] = Field(..., description="目标列表")
    total: int = Field(..., description="总数量")
    active_count: int = Field(..., description="活跃目标数量")

# =============== 时间记录模型 ===============

class TimeRecordCreate(BaseModel):
    input_text: str = Field(..., min_length=1, description="自然语言时间描述")
    manual_goal_id: Optional[str] = Field(None, description="手动指定关联目标ID")

class TimeRecordUpdate(BaseModel):
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    activity: Optional[str] = Field(None, description="活动类型")
    goal_id: Optional[str] = Field(None, description="关联目标ID")

class MatchedGoal(BaseModel):
    id: str = Field(..., description="目标ID")
    title: str = Field(..., description="目标标题")
    progress_after: int = Field(..., description="更新后的实际时长")
    progress_percentage: int = Field(..., description="完成百分比")

class TimeRecord(BaseModel):
    id: str = Field(..., description="记录ID")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    duration: int = Field(..., description="时长(分钟)")
    activity: str = Field(..., description="活动类型")
    category: CategoryEnum = Field(..., description="活动分类")
    description: str = Field(..., description="描述")
    confidence: int = Field(..., ge=0, le=100, description="解析置信度")
    parsing_method: ParsingMethodEnum = Field(..., description="解析方法")
    matched_goal: Optional[MatchedGoal] = Field(None, description="匹配的目标")
    created_at: datetime = Field(..., description="创建时间")

class TimeRecordListResponse(BaseModel):
    records: List[TimeRecord] = Field(..., description="时间记录列表")
    total: int = Field(..., description="总记录数")
    total_duration: int = Field(..., description="总时长(分钟)")

# =============== 报告统计模型 ===============

class CategoryStats(BaseModel):
    duration: int = Field(..., description="时长(分钟)")
    percentage: float = Field(..., description="占比")

class ActivityStats(BaseModel):
    activity: str = Field(..., description="活动名称")
    duration: int = Field(..., description="时长(分钟)")

class GoalProgress(BaseModel):
    goal_id: str = Field(..., description="目标ID")
    title: str = Field(..., description="目标标题")
    progress: int = Field(..., description="实际投入时长")
    estimated: int = Field(..., description="预估时长")
    percentage: int = Field(..., description="完成百分比")

class DailyReport(BaseModel):
    report_date: DateType = Field(..., description="报告日期")
    total_records: int = Field(..., description="记录条数")
    total_duration: int = Field(..., description="总时长(分钟)")
    efficiency_rate: float = Field(..., description="有效率")
    category_stats: Dict[str, CategoryStats] = Field(..., description="分类统计")
    activity_stats: List[ActivityStats] = Field(..., description="活动统计")
    goal_progress: List[GoalProgress] = Field(..., description="目标进度")

class DailyBreakdown(BaseModel):
    breakdown_date: DateType = Field(..., description="日期")
    duration: int = Field(..., description="时长(分钟)")

class CompletedGoal(BaseModel):
    title: str = Field(..., description="目标标题")
    estimated_time: int = Field(..., description="预估时长")
    actual_time: int = Field(..., description="实际时长")

class WeeklyReport(BaseModel):
    week: str = Field(..., description="周标识(如2025-W30)")
    date_range: List[DateType] = Field(..., description="日期范围")
    total_duration: int = Field(..., description="总时长(分钟)")
    efficiency_rate: float = Field(..., description="有效率")
    daily_breakdown: List[DailyBreakdown] = Field(..., description="每日分解")
    category_summary: Dict[str, CategoryStats] = Field(..., description="分类汇总")
    completed_goals: List[CompletedGoal] = Field(..., description="已完成目标")

# 验证器
class GoalCreateValidated(GoalCreate):
    @field_validator('deadline')
    @classmethod
    def validate_deadline(cls, v):
        if v < DateType.today():
            raise ValueError('截止日期不能早于今天')
        return v