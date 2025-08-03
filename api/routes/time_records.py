"""
时间记录API路由
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import date, datetime
from dateutil.parser import parse as parse_datetime
import logging

from api.models.schemas import (
    ApiResponse, TimeRecord, TimeRecordCreate, TimeRecordUpdate, TimeRecordListResponse
)
from api.services.time_agent_service import TimeAgentService
from api.middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", response_model=ApiResponse)
async def create_time_record(
    record_data: TimeRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """创建时间记录"""
    try:
        service = TimeAgentService()
        record = await service.create_time_record(record_data)
        
        return ApiResponse(
            success=True,
            data=record.model_dump()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建时间记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建时间记录失败"
        )

@router.get("", response_model=ApiResponse)
async def get_time_records(
    target_date: Optional[date] = Query(None, description="目标日期"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: dict = Depends(get_current_user)
):
    """获取时间记录列表"""
    try:
        service = TimeAgentService()
        records, total = await service.get_time_records(
            target_date=target_date,
            limit=limit,
            offset=offset
        )
        
        # 计算总时长
        total_duration = sum(record.duration for record in records)
        
        response_data = TimeRecordListResponse(
            records=records,
            total=total,
            total_duration=total_duration
        )
        
        return ApiResponse(
            success=True,
            data=response_data.model_dump(),
            meta={
                "page": offset // limit + 1,
                "limit": limit,
                "total": total
            }
        )
        
    except Exception as e:
        logger.error(f"获取时间记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取时间记录失败"
        )

@router.get("/{record_id}", response_model=ApiResponse)
async def get_time_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取单个时间记录详情"""
    try:
        service = TimeAgentService()
        record = await service.get_time_record(record_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="时间记录不存在"
            )
        
        return ApiResponse(
            success=True,
            data=record.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取时间记录详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取时间记录详情失败"
        )

@router.put("/{record_id}", response_model=ApiResponse)
async def update_time_record(
    record_id: str,
    record_data: TimeRecordUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新时间记录"""
    try:
        service = TimeAgentService()
        
        # 构建更新数据
        update_data = {}
        if record_data.start_time:
            update_data['start_time'] = record_data.start_time
        if record_data.end_time:
            update_data['end_time'] = record_data.end_time
        if record_data.activity:
            update_data['activity'] = record_data.activity
        
        # 如果只有开始时间或结束时间之一，需要先获取原记录
        if (record_data.start_time and not record_data.end_time) or (record_data.end_time and not record_data.start_time):
            original_record = await service.get_time_record(record_id)
            if not original_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="时间记录不存在"
                )
            
            if not record_data.start_time:
                update_data['start_time'] = parse_datetime(original_record.start_time) if isinstance(original_record.start_time, str) else original_record.start_time
            if not record_data.end_time:
                update_data['end_time'] = parse_datetime(original_record.end_time) if isinstance(original_record.end_time, str) else original_record.end_time
            if not record_data.activity:
                update_data['activity'] = original_record.activity
            
            update_data['description'] = original_record.description
        
        updated_record = await service.update_time_record(record_id, update_data)
        
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="时间记录不存在"
            )
        
        return ApiResponse(
            success=True,
            data=updated_record.model_dump()
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"更新时间记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新时间记录失败"
        )

@router.delete("/{record_id}", response_model=ApiResponse)
async def delete_time_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    """删除时间记录"""
    try:
        service = TimeAgentService()
        success = await service.delete_time_record(record_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="时间记录不存在或删除失败"
            )
        
        return ApiResponse(
            success=True,
            data={"message": "时间记录已删除"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除时间记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除时间记录失败"
        )

@router.post("/batch", response_model=ApiResponse)
async def create_batch_time_records(
    records_data: list[TimeRecordCreate],
    current_user: dict = Depends(get_current_user)
):
    """批量创建时间记录"""
    try:
        service = TimeAgentService()
        created_records = []
        failed_records = []
        
        for i, record_data in enumerate(records_data):
            try:
                record = await service.create_time_record(record_data)
                created_records.append(record)
            except Exception as e:
                failed_records.append({
                    "index": i,
                    "input_text": record_data.input_text,
                    "error": str(e)
                })
        
        response_data = {
            "created_count": len(created_records),
            "failed_count": len(failed_records),
            "created_records": [record.model_dump() for record in created_records],
            "failed_records": failed_records
        }
        
        return ApiResponse(
            success=True,
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"批量创建时间记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量创建时间记录失败"
        )