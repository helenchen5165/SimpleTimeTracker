"""
仪表板API路由
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from datetime import date
import logging

from api.models.schemas import ApiResponse
from api.services.time_agent_service import TimeAgentService
from api.middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/today-overview", response_model=ApiResponse)
async def get_today_overview(
    current_user: dict = Depends(get_current_user)
):
    """获取今日概览数据"""
    try:
        service = TimeAgentService()
        today = date.today()
        
        # 获取今日时间记录
        records, total_records = await service.get_time_records(
            target_date=today,
            limit=100  # 获取今天所有记录
        )
        
        # 计算今日总时长
        total_duration = sum(record.duration for record in records)
        
        # 获取活跃目标数量
        active_goals = await service.get_active_goals(today)
        active_goals_count = len(active_goals)
        
        # 计算分类分布
        category_breakdown = {}
        for record in records:
            category = record.category
            if category not in category_breakdown:
                category_breakdown[category] = 0
            category_breakdown[category] += record.duration
        
        # 计算今日效率（生产+投资类别占比）
        productive_time = category_breakdown.get("生产", 0) + category_breakdown.get("投资", 0)
        efficiency_rate = (productive_time / total_duration * 100) if total_duration > 0 else 0
        
        # 获取热门活动（前3个）
        activity_stats = {}
        for record in records:
            activity = record.activity
            if activity not in activity_stats:
                activity_stats[activity] = 0
            activity_stats[activity] += record.duration
        
        top_activities = sorted(activity_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 获取有进度的目标
        goals_with_progress = [goal for goal in active_goals if goal.actual_time > 0]
        
        overview_data = {
            "today_records": total_records,
            "today_duration": total_duration,
            "active_goals": active_goals_count,
            "efficiency_rate": round(efficiency_rate, 1),
            "category_breakdown": category_breakdown,
            "top_activities": [
                {"activity": activity, "duration": duration}
                for activity, duration in top_activities
            ],
            "goals_with_progress": len(goals_with_progress),
            "recent_records": records[:5] if records else []  # 最近5条记录
        }
        
        return ApiResponse(
            success=True,
            data=overview_data
        )
        
    except Exception as e:
        logger.error(f"获取今日概览失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取今日概览失败"
        )

@router.get("/weekly-summary", response_model=ApiResponse)
async def get_weekly_summary(
    current_user: dict = Depends(get_current_user)
):
    """获取本周汇总数据"""
    try:
        service = TimeAgentService()
        today = date.today()
        
        # 获取本周报告
        weekly_report = await service.generate_weekly_report(today)
        
        # 提取关键指标
        summary_data = {
            "week_identifier": weekly_report.week,
            "total_duration": weekly_report.total_duration,
            "efficiency_rate": weekly_report.efficiency_rate,
            "daily_average": weekly_report.total_duration // 7,
            "completed_goals": len(weekly_report.completed_goals),
            "category_summary": weekly_report.category_summary
        }
        
        return ApiResponse(
            success=True,
            data=summary_data
        )
        
    except Exception as e:
        logger.error(f"获取周汇总失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取周汇总失败"
        )