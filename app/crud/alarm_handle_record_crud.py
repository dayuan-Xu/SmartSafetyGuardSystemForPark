# file:app\crud\alarm_handle_record_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.DB_models.alarm_handle_record_db import AlarmHandleRecordDB
from typing import Optional, List


def get_alarm_handle_record(db: Session, alarm_id: int) -> Optional[AlarmHandleRecordDB]:
    """
    根据告警ID获取对应告警处理记录

    Args:
        db: 数据库会话
        alarm_id: 处理记录ID

    Returns:
        Optional[AlarmHandleRecordDB]: 告警处理记录对象或None
    """
    return db.query(AlarmHandleRecordDB).filter(AlarmHandleRecordDB.alarm_id == alarm_id).all()


