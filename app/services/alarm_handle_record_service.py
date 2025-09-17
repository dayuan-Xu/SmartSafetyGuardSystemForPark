#file:app\services\alarm_handle_record_service.py
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.alarm_handle_record_pydantic import AlarmHandleRecordResponse
from app.crud.alarm_handle_record_crud import (
    get_alarm_handle_record as crud_get_alarm_handle_record,
)


class AlarmHandleRecordService:
    @staticmethod
    def get_handle_record_by_id(db: Session, handle_id: int) -> Result[AlarmHandleRecordResponse]:
        """
        根据处理记录ID获取单个告警处理记录

        Args:
            db: 数据库会话
            handle_id: 处理记录ID

        Returns:
            Result[AlarmHandleRecordResponse]: 包含告警处理记录信息的响应对象
        """
        db_handle_record = crud_get_alarm_handle_record(db, handle_id)
        if not db_handle_record:
            return Result.ERROR(f"AlarmHandleRecord not found with given id={handle_id}")
        return Result.SUCCESS(db_handle_record)

