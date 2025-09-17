#file:app\api\v1\endpoints\alarm_handle_record_router.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.alarm_handle_record_pydantic import AlarmHandleRecordResponse
from app.services.alarm_handle_record_service import AlarmHandleRecordService

router = APIRouter()

# 1. GET /api/v1/alarm_handle_records/{handle_id}：获取单个告警处理记录
@router.get("/{handle_id}", response_model=Result[AlarmHandleRecordResponse], summary="获取单个告警处理记录")
def read_alarm_handle_record(
    handle_id: int = Path(..., title="处理记录ID", description="处理记录唯一标识"),
    db: Session = Depends(get_db)
):
    """
    根据处理记录ID获取单个告警处理记录

    Args:
        handle_id: 处理记录唯一标识
        db: 数据库会话对象

    Returns:
        Result[AlarmHandleRecordResponse]: 包含告警处理记录信息的结果对象
    """
    return AlarmHandleRecordService.get_handle_record_by_id(db, handle_id)

