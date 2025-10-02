import asyncio
from typing import List
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.alarm_handle_record_pydantic import (
    AlarmHandleRecordResponse,
    AlarmHandleRecordCreate
)
from app.crud.alarm_handle_record_crud import (
    get_alarm_handle_records as crud_get_alarm_handle_records,
    create_alarm_handle_record as crud_create_alarm_handle_record
)
from app.crud.alarm_crud import update_alarm_status
from app.services.storage_service import StorageService
from app.services.thread_pool_manager import executor as db_executor


class AlarmHandleRecordService:
    @staticmethod
    async def get_handle_records_by_alarm_id(db: Session, alarm_id: int) -> Result[List[AlarmHandleRecordResponse]]:
        """
        根据告警ID获取该告警的所有处理记录

        Args:
            db: 数据库会话
            alarm_id: 告警ID

        Returns:
            Result[List[AlarmHandleRecordResponse]]: 包含告警处理记录列表的响应对象
        """
        # 使用线程池执行数据库操作
        db_handle_records = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_get_alarm_handle_records, db, alarm_id
        )
        if not db_handle_records:
            return Result.ERROR(f"No alarm handle records found for alarm id={alarm_id}")
        return Result.SUCCESS(db_handle_records)

    @classmethod
    async def create_handle_record(cls, db: Session, record_create: AlarmHandleRecordCreate) -> Result[AlarmHandleRecordResponse]:
        """
        创建告警处理记录

        Args:
            db: 数据库会话
            record_create: 告警处理记录创建数据

        Returns:
            Result[AlarmHandleRecordResponse]: 包含创建的告警处理记录的响应对象
        """
        try:
            def _create_record():
                # 创建告警处理记录
                created_record = crud_create_alarm_handle_record(db, record_create)

                # 根据处理动作类型更新对应告警记录的状态
                if record_create.handle_action == 1:  # 派单处理
                    update_alarm_status(db, record_create.alarm_id, 2)  # 告警状态为2表示"处理中（已派单）"
                elif record_create.handle_action == 2:  # 标记已解决
                    update_alarm_status(db, record_create.alarm_id, 3)  # 告警状态为3表示"处理完成"
                elif record_create.handle_action == 0:  # 标记误报
                    update_alarm_status(db, record_create.alarm_id, 1)  # 告警状态为1表示"确认误报"

                return Result.SUCCESS(created_record, "处理记录创建成功")
            
            # 使用线程池执行数据库操作
            return await asyncio.get_event_loop().run_in_executor(db_executor, _create_record)
        except Exception as e:
            return Result.ERROR(f"处理记录创建失败: {str(e)}")

    @classmethod
    async def upload_attachment(cls, attachment_data) -> Result[str]:
        """
        上传告警处理附件并返回URL

        Args:
            attachment_data: 附件数据（包含Base64编码的内容和文件扩展名）

        Returns:
            Result[str]: 包含文件URL的响应对象
        """
        try:
            def _upload_attachment():
                # 上传附件到OSS并获取URL
                file_url = StorageService.upload_alarm_attachment(
                    attachment_data.file_content,
                    attachment_data.file_extension
                )
                return Result.SUCCESS(file_url, "附件上传成功")
            
            # 使用线程池执行存储操作
            return await asyncio.get_event_loop().run_in_executor(db_executor, _upload_attachment)
        except Exception as e:
            return Result.ERROR(f"附件上传失败: {str(e)}")