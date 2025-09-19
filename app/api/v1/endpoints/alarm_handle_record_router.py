from typing import List
from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.alarm_handle_record_pydantic import AlarmHandleRecordResponse, AlarmHandleRecordCreate,AlarmAttachmentUpload
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


# 2. POST /api/v1/alarm_handle_records/upload_attachment：上传告警处理附件
@router.post("/upload_attachment", response_model=Result[str], summary="上传告警处理附件")
def upload_attachment(
        attachment_data: AlarmAttachmentUpload,
        db: Session = Depends(get_db)
):
    """
    上传告警处理附件并返回OSS URL

    参数:
    - attachment_data: 包含Base64编码文件内容和文件扩展名的对象

    返回:
    - 文件的OSS URL
    """
    return AlarmHandleRecordService.upload_attachment(db, attachment_data)


# 3. POST /api/v1/alarm_handle_records：创建告警处理记录
@router.post("/", response_model=Result[AlarmHandleRecordResponse], summary="创建告警处理记录")
def create_handle_record(
        record_create: AlarmHandleRecordCreate,
        db: Session = Depends(get_db)
):
    """
    创建新的告警处理记录
    """
    return AlarmHandleRecordService.create_handle_record(db, record_create)