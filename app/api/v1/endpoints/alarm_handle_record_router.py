from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.alarm_handle_record_pydantic import AlarmHandleRecordResponse, AlarmHandleRecordCreate,AlarmAttachmentUpload
from app.services.alarm_handle_record_service import AlarmHandleRecordService

router = APIRouter()

# 1. GET /api/v1/alarm_handle_records/{alarm_id}：获取某个告警的所有处理记录
@router.get("/{alarm_id}", response_model=Result[List[AlarmHandleRecordResponse]], summary="获取告警处理记录列表", status_code=status.HTTP_200_OK)
async def read_alarm_handle_record(
    alarm_id: int = Path(..., title="告警ID", description="告警记录唯一标识"),
    db: Session = Depends(get_db)
):
    """
    根据告警ID获取该告警的处理记录列表

    Args:
        alarm_id (int): 告警记录唯一标识
        db (Session): 数据库会话

    Returns:
        Result[List[AlarmHandleRecordResponse]]: 包含告警处理记录列表的统一响应结果
    """
    result = await AlarmHandleRecordService.get_handle_records_by_alarm_id(db, alarm_id)
    return result


# 2. POST /api/v1/alarm_handle_records/upload_attachment：上传告警处理附件
@router.post("/upload_attachment", response_model=Result[str], summary="上传告警处理附件", status_code=status.HTTP_201_CREATED)
async def upload_attachment(
        attachment_data: AlarmAttachmentUpload,
):
    """
    上传告警处理附件并返回OSS URL

    参数:
    - attachment_data（AlarmAttachmentUpload）: 包含Base64编码文件内容和文件扩展名的对象

    返回:
        Result[str]:包含文件的OSS URL的统一响应结果
    """
    result = await AlarmHandleRecordService.upload_attachment(attachment_data)
    return result


# 3. POST /api/v1/alarm_handle_records：创建告警处理记录
@router.post("/", response_model=Result[AlarmHandleRecordResponse], summary="创建告警处理记录", status_code=status.HTTP_201_CREATED)
async def create_handle_record(
        record_create: AlarmHandleRecordCreate,
        db: Session = Depends(get_db)
):
    """
    创建新的告警处理记录

    Args:
        record_create (AlarmHandleRecordCreate): 告警处理记录创建信息
        db (Session): 数据库会话

    Returns:
        Result[AlarmHandleRecordResponse]: 包含新创建的告警处理记录的统一响应结果
    """
    result = await AlarmHandleRecordService.create_handle_record(db, record_create)
    return result