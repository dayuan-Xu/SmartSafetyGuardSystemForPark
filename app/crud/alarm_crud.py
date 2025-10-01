from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.DB_models.alarm_db import AlarmDB
from app.DB_models.alarm_handle_record_db import AlarmHandleRecordDB
from app.DB_models.camera_info_db import CameraInfoDB
from app.DB_models.user_db import UserDB
from app.DB_models.park_area_db import ParkAreaDB


def create_alarm(
    db: Session,
    camera_id: int,
    alarm_type: int,
    alarm_status: int,
    alarm_time: datetime,
    snapshot_url: str,
):
    """
    创建一个新的报警记录
    alarm_type # 0-安全规范（未戴安全帽/未穿反光衣） 1-区域入侵（人/车） 2-火警（火焰+烟雾）
    """
    new_alarm = AlarmDB(
        camera_id=camera_id,
        alarm_type=alarm_type,
        alarm_status=alarm_status,
        alarm_time=alarm_time,
        snapshot_url=snapshot_url,
    )
    db.add(new_alarm)
    db.commit()
    db.refresh(new_alarm)
    return new_alarm


def get_alarm_by_id(db: Session, alarm_id: int):
    """
    根据报警ID获取报警记录
    """
    return db.query(AlarmDB).filter(AlarmDB.alarm_id == alarm_id).first()


def get_alarms_by_camera_id(db: Session, camera_id: int, skip: int = 0, limit: int = 100):
    """
    根据摄像头ID获取报警记录列表（支持分页）
    """
    return db.query(AlarmDB).filter(AlarmDB.camera_id == camera_id).offset(skip).limit(limit).all()


def get_alarms_with_condition(
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        alarm_type: Optional[int] = None,
        alarm_status: Optional[int] = None,
        skip: int = 0,
        limit: int = 10
):
    """
    根据条件获取报警记录列表（支持分页），包含摄像头信息和处理记录信息
    """
    # 构建子查询，获取每个alarm_id的最新处理记录
    latest_handle_subquery = (
        db.query(
            AlarmHandleRecordDB.alarm_id,
            func.max(AlarmHandleRecordDB.handle_time).label('latest_handle_time')
        )
        .group_by(AlarmHandleRecordDB.alarm_id)
        .subquery()
    )

    # 构建联表查询
    query = db.query(
        AlarmDB,
        ParkAreaDB.park_area,
        CameraInfoDB.camera_name,
        UserDB.name.label('handle_user_name')
    ).outerjoin(
        CameraInfoDB, AlarmDB.camera_id == CameraInfoDB.camera_id
    ).outerjoin(
        ParkAreaDB, CameraInfoDB.park_area_id == ParkAreaDB.park_area_id
    ).outerjoin(
        latest_handle_subquery, 
        AlarmDB.alarm_id == latest_handle_subquery.c.alarm_id
    ).outerjoin(
        AlarmHandleRecordDB,
        and_(
            AlarmDB.alarm_id == AlarmHandleRecordDB.alarm_id,
            AlarmHandleRecordDB.handle_time == latest_handle_subquery.c.latest_handle_time
        )
    ).outerjoin(
        UserDB, AlarmHandleRecordDB.handler_user_id == UserDB.user_id
    )

    # 添加时间范围条件
    if start_time and end_time:
        query = query.filter(AlarmDB.alarm_time.between(start_time, end_time))
    elif start_time:
        query = query.filter(AlarmDB.alarm_time >= start_time)
    elif end_time:
        query = query.filter(AlarmDB.alarm_time <= end_time)

    # 添加告警类型条件
    if alarm_type is not None:
        query = query.filter(AlarmDB.alarm_type == alarm_type)

    # 添加告警状态条件
    if alarm_status is not None:
        query = query.filter(AlarmDB.alarm_status == alarm_status)

    # 分组以避免重复记录（一个告警可能有多条处理记录）
    query = query.group_by(
        AlarmDB.alarm_id,
        AlarmDB.camera_id,
        AlarmDB.alarm_type,
        AlarmDB.alarm_status,
        AlarmDB.alarm_time,
        AlarmDB.alarm_end_time,
        AlarmDB.snapshot_url,
        AlarmDB.create_time,
        AlarmDB.update_time,
        ParkAreaDB.park_area,
        CameraInfoDB.camera_name,
        UserDB.name
    )

    # 返回计数和分页结果
    count = query.count()
    alarms_with_details = query.offset(skip).limit(limit).all()
    return count, alarms_with_details


def update_alarm_status(db: Session, alarm_id: int, alarm_status: int):
    """
    更新报警状态
    """
    alarm = db.query(AlarmDB).filter(AlarmDB.alarm_id == alarm_id).first()
    if alarm:
        alarm.alarm_status = alarm_status
        alarm.update_time = datetime.now()
        db.commit()
        db.refresh(alarm)
    return alarm

def update_alarm_end_time(db: Session, alarm_id: int, alarm_end_time:datetime):
    """
    更新报警停止继续发生的时间
    """
    alarm = db.query(AlarmDB).filter(AlarmDB.alarm_id == alarm_id).first()
    if alarm:
        alarm.alarm_end_time = alarm_end_time
        alarm.update_time = datetime.now()
        db.commit()
        db.refresh(alarm)
    return alarm


def delete_alarm(db: Session, alarm_id: int):
    """
    删除指定的报警记录
    """
    alarm = db.query(AlarmDB).filter(AlarmDB.alarm_id == alarm_id).first()
    if alarm:
        db.delete(alarm)
        db.commit()
    return alarm


def delete_alarms_and_related_records(db: Session, alarm_ids: List[int]) -> int:
    """
    批量删除告警记录及其关联的处理记录

    Args:
        db: 数据库会话
        alarm_ids: 告警ID列表

    Returns:
        int: 成功删除的告警记录数
    """
    deleted_count = 0

    try:
        # 先删除所有关联的告警处理记录
        for alarm_id in alarm_ids:
            db.query(AlarmHandleRecordDB).filter(AlarmHandleRecordDB.alarm_id == alarm_id).delete()

        # 再删除告警记录
        deleted_count = db.query(AlarmDB).filter(AlarmDB.alarm_id.in_(alarm_ids)).delete(synchronize_session=False)

        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    return deleted_count