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
@router.get("/{alarm_id}", response_model=Result[List[AlarmHandleRecordResponse]], summary="获取告警处理记录列表")
def read_alarm_handle_record(
    alarm_id: int = Path(..., title="告警ID", description="告警记录唯一标识"),
    db: Session = Depends(get_db)
):
    """
    根据告警ID获取相关处理记录列表
    """
    return AlarmHandleRecordService.get_handle_records_by_alarm_id(db, alarm_id)


