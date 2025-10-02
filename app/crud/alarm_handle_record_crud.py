from sqlalchemy.orm import Session
from app.DB_models.alarm_handle_record_db import AlarmHandleRecordDB
from typing import Optional, List
from app.JSON_schemas.alarm_handle_record_pydantic import AlarmHandleRecordCreate

from app.JSON_schemas.alarm_handle_record_pydantic import AlarmHandleRecordCreate


def get_alarm_handle_records(db: Session, alarm_id: int) -> List[AlarmHandleRecordDB]:
    """
    根据告警ID获取该告警的所有处理记录

    Args:
        db (Session): 数据库会话
        alarm_id (int): 告警ID

    Returns:
        List[AlarmHandleRecordDB]: 告警处理记录对象列表
    """
    return db.query(AlarmHandleRecordDB).filter(AlarmHandleRecordDB.alarm_id == alarm_id).all()

def create_alarm_handle_record(db: Session, record_create: AlarmHandleRecordCreate) -> AlarmHandleRecordDB:
    """
    创建新的告警处理记录

    Args:
        db (Session): 数据库会话
        record_create (AlarmHandleRecordCreate): 告警处理记录创建数据

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