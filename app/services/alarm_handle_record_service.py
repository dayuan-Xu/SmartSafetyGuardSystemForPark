#file:app\services\alarm_handle_record_service.py
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.alarm_handle_record_pydantic import AlarmHandleRecordResponse
from app.crud.alarm_handle_record_crud import (
    get_alarm_handle_record as crud_get_alarm_handle_record,
)


class AlarmHandleRecordService:
    @staticmethod
    def get_handle_records_by_alarm_id(db: Session, alarm_id: int) -> Result[AlarmHandleRecordResponse]:
        """
        根据告警ID获取单个对应所有告警处理记录

        Args:
            db: 数据库会话
            alarm_id: 处理记录ID

        Returns:
            Result[AlarmHandleRecordResponse]: 包含告警处理记录信息的响应对象
        """
        db_handle_record = crud_get_alarm_handle_record(db, alarm_id)
        if not db_handle_record:
            return Result.ERROR(f"AlarmHandleRecord not found with given alarm id={alarm_id}")
        return Result.SUCCESS(db_handle_record)

