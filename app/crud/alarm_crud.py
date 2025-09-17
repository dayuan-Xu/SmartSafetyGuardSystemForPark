from datetime import datetime
from sqlalchemy.orm import Session
from app.DB_models.alarm_db import AlarmDB

def create_alarm(
    db: Session,
    camera_id: int,
    alarm_type: int,
    alarm_status: int,
    alarm_time: datetime,
    snapshot_url: str,
    video_clip_url: str
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
        video_clip_url=video_clip_url
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
