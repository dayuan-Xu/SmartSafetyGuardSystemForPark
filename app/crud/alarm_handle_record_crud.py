from sqlalchemy.orm import Session
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

def create_alarm_handle_record(db: Session, record_create: AlarmHandleRecordCreate) -> AlarmHandleRecordDB:
    """
    创建新的告警处理记录

    Args:
        db: 数据库会话
        record_create: 告警处理记录创建数据

    Returns:
        AlarmHandleRecordDB: 新创建的告警处理记录对象
    """
    # 将Pydantic模型转换为数据库模型
    db_record = AlarmHandleRecordDB(**record_create.model_dump(exclude_unset=True))

    # 添加到数据库
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record