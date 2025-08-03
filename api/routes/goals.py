"""
目标管理API路由
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import date
import logging

from api.models.schemas import (
    ApiResponse, Goal, GoalCreate, GoalUpdate, GoalListResponse
)
from api.services.time_agent_service import TimeAgentService
from api.middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=ApiResponse)
async def get_goals(
    status_filter: Optional[str] = Query(None, alias="status", description="状态过滤"),
    deadline: Optional[date] = Query(None, description="截止日期过滤"),
    current_user: dict = Depends(get_current_user)
):
    """获取目标列表"""
    try:
        service = TimeAgentService()
        
        # 获取活跃目标
        goals = await service.get_active_goals()
        
        # 应用过滤条件
        if status_filter:
            if status_filter.lower() == 'active':
                # "active" 表示活跃目标，包括 Planned 和 In Progress
                goals = [g for g in goals if g.status in ["Planned", "In Progress"]]
            else:
                # 其他状态直接匹配
                goals = [g for g in goals if g.status.lower() == status_filter.lower()]
        
        if deadline:
            goals = [g for g in goals if g.deadline <= deadline]
        
        # 统计信息
        active_count = len([g for g in goals if g.status != "Completed"])
        
        response_data = GoalListResponse(
            goals=goals,
            total=len(goals),
            active_count=active_count
        )
        
        return ApiResponse(
            success=True,
            data=response_data.dict()
        )
        
    except Exception as e:
        logger.error(f"获取目标列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取目标列表失败"
        )

@router.post("", response_model=ApiResponse)
async def create_goal(
    goal_data: GoalCreate,
    current_user: dict = Depends(get_current_user)
):
    """创建目标"""
    try:
        service = TimeAgentService()
        goal = await service.create_goal(goal_data)
        
        return ApiResponse(
            success=True,
            data=goal.dict()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建目标失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建目标失败"
        )

@router.get("/{goal_id}", response_model=ApiResponse)
async def get_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取单个目标详情"""
    try:
        # TODO: 实现获取单个目标的逻辑
        # 暂时返回模拟数据
        goal = Goal(
            id=goal_id,
            title="学习Python编程",
            deadline=date.today(),
            estimated_time=300,
            actual_time=120,
            progress=40,
            priority="High",
            status="In Progress",
            created_at="2025-07-28T10:00:00Z"
        )
        
        return ApiResponse(
            success=True,
            data=goal.dict()
        )
        
    except Exception as e:
        logger.error(f"获取目标详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取目标详情失败"
        )

@router.put("/{goal_id}", response_model=ApiResponse)
async def update_goal(
    goal_id: str,
    goal_data: GoalUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新目标"""
    try:
        service = TimeAgentService()
        goal = await service.update_goal(goal_id, goal_data)
        
        return ApiResponse(
            success=True,
            data=goal.dict()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"更新目标失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新目标失败"
        )

@router.delete("/{goal_id}", response_model=ApiResponse)
async def delete_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """删除目标"""
    try:
        service = TimeAgentService()
        success = await service.delete_goal(goal_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="目标不存在"
            )
        
        return ApiResponse(
            success=True,
            data={"message": "目标已删除"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除目标失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除目标失败"
        )

@router.get("/{goal_id}/progress", response_model=ApiResponse)
async def get_goal_progress(
    goal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取目标进度详情"""
    try:
        # TODO: 实现获取目标进度的详细逻辑
        progress_data = {
            "goal_id": goal_id,
            "total_time_records": 5,
            "recent_activities": [
                {
                    "date": "2025-07-28",
                    "duration": 60,
                    "activity": "学习Python基础"
                },
                {
                    "date": "2025-07-27", 
                    "duration": 90,
                    "activity": "练习Python语法"
                }
            ],
            "daily_progress": [
                {"date": "2025-07-21", "minutes": 0},
                {"date": "2025-07-22", "minutes": 30},
                {"date": "2025-07-23", "minutes": 60},
                {"date": "2025-07-24", "minutes": 45},
                {"date": "2025-07-25", "minutes": 90},
                {"date": "2025-07-26", "minutes": 60},
                {"date": "2025-07-27", "minutes": 90}
            ]
        }
        
        return ApiResponse(
            success=True,
            data=progress_data
        )
        
    except Exception as e:
        logger.error(f"获取目标进度失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取目标进度失败"
        )