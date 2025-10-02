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

    Args:
        db (Session): 数据库会话
        camera_id (int): 摄像头ID
        alarm_type (int): 告警类型 # 0-安全规范（未戴安全帽/未穿反光衣） 1-区域入侵（人/车） 2-火警（火焰+烟雾）
        alarm_status (int): 告警状态
        alarm_time (datetime): 告警触发时间
        snapshot_url (str): 报警截图URL

    Returns:
        AlarmDB: 新创建的报警记录对象
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

    Args:
        db (Session): 数据库会话
        alarm_id (int): 报警ID

    Returns:
        AlarmDB: 报警记录对象或None
    """
    return db.query(AlarmDB).filter(AlarmDB.alarm_id == alarm_id).first()

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

    Args:
        db (Session): 数据库会话
        start_time (Optional[datetime]): 告警触发时间左边界
        end_time (Optional[datetime]): 告警触发时间右边界
        alarm_type (Optional[int]): 告警类型
        alarm_status (Optional[int]): 告警状态
        skip (int): 跳过的记录数，默认为0
        limit (int): 限制返回的记录数，默认为10

    Returns:
        tuple: (总数, 告警记录列表)
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
        CameraInfoDB.camera_name,
        ParkAreaDB.park_area,
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

    # 返回计数和分页结果
    count = query.count()
    alarms_with_details = query.offset(skip).limit(limit).all()
    return count, alarms_with_details


def get_today_alarm_counts(db: Session):
    """
    获取本日告警统计信息
    
    Args:
        db (Session): 数据库会话
        
    Returns:
        list: 包含告警类型和数量的元组列表
    """
    # 获取今天的开始和结束时间
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    # 查询本日各类型告警的数量
    results = db.query(
        AlarmDB.alarm_type,
        func.count(AlarmDB.alarm_id).label('alarm_number')
    ).filter(
        AlarmDB.alarm_time.between(start_of_day, end_of_day)
    ).group_by(
        AlarmDB.alarm_type
    ).all()
    
    # 确保返回所有类型的告警数据（包括数量为0的类型）
    alarm_counts = {0: 0, 1: 0, 2: 0}
    for alarm_type, count in results:
        alarm_counts[alarm_type] = count
    
    # 转换为按类型排序的列表
    sorted_results = [(alarm_type, alarm_counts[alarm_type]) for alarm_type in sorted(alarm_counts.keys())]
    
    return sorted_results


def get_today_alarm_handle_stats(db: Session):
    """
    获取本日告警处理统计信息（处理率和未处理数）
    
    Args:
        db (Session): 数据库会话
        
    Returns:
        tuple: (今日告警总数, 今日已处理告警数, 今日未处理告警数)
    """
    # 获取今天的开始和结束时间
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    # 查询今日告警总数
    total_count = db.query(AlarmDB).filter(
        AlarmDB.alarm_time.between(start_of_day, end_of_day)
    ).count()
    
    # 查询今日已处理告警数（状态为1确认误报、3处理完成）
    handled_count = db.query(AlarmDB).filter(
        AlarmDB.alarm_time.between(start_of_day, end_of_day),
        AlarmDB.alarm_status.in_([1, 3])
    ).count()
    
    # 查询今日未处理告警数（状态为0未处理）
    unhandled_count = db.query(AlarmDB).filter(
        AlarmDB.alarm_time.between(start_of_day, end_of_day),
        AlarmDB.alarm_status == 0
    ).count()
    
    return total_count, handled_count, unhandled_count


def get_top3_alarm_areas(db: Session):
    """
    获取告警数位居前3的园区区域统计信息
    
    Args:
        db (Session): 数据库会话
        
    Returns:
        list: 包含园区区域名称和告警数量的元组列表，按告警数量降序排列，最多3条
    """
    # 查询各园区区域的告警数量，按数量降序排列，取前3条
    results = db.query(
        ParkAreaDB.park_area,
        func.count(AlarmDB.alarm_id).label('alarm_count')
    ).join(
        CameraInfoDB, ParkAreaDB.park_area_id == CameraInfoDB.park_area_id
    ).join(
        AlarmDB, CameraInfoDB.camera_id == AlarmDB.camera_id
    ).group_by(
        ParkAreaDB.park_area
    ).order_by(
        func.count(AlarmDB.alarm_id).desc()
    ).limit(3).all()
    
    return results


def get_all_alarm_counts(db: Session):
    """
    获取所有告警统计信息
    
    Args:
        db (Session): 数据库会话
        
    Returns:
        list: 包含告警类型和数量的元组列表
    """
    # 查询所有告警中各类型告警的数量
    results = db.query(
        AlarmDB.alarm_type,
        func.count(AlarmDB.alarm_id).label('alarm_number')
    ).group_by(
        AlarmDB.alarm_type
    ).all()
    
    # 确保返回所有类型的告警数据（包括数量为0的类型）
    alarm_counts = {0: 0, 1: 0, 2: 0}
    for alarm_type, count in results:
        alarm_counts[alarm_type] = count
    
    # 转换为按类型排序的列表
    sorted_results = [(alarm_type, alarm_counts[alarm_type]) for alarm_type in sorted(alarm_counts.keys())]
    
    return sorted_results


def update_alarm_status(db: Session, alarm_id: int, alarm_status: int):
    """
    更新报警状态

    Args:
        db (Session): 数据库会话
        alarm_id (int): 报警ID
        alarm_status (int): 新的报警状态

    Returns:
        AlarmDB: 更新后的报警记录对象或None
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

    Args:
        db (Session): 数据库会话
        alarm_id (int): 报警ID
        alarm_end_time (datetime): 报警结束时间

    Returns:
        AlarmDB: 更新后的报警记录对象或None
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

    Args:
        db (Session): 数据库会话
        alarm_id (int): 报警ID

    Returns:
        AlarmDB: 被删除的报警记录对象或None
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
        db (Session): 数据库会话
        alarm_ids (List[int]): 告警ID列表

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


def get_recent_unresolved_alarms(db: Session, limit: int = 5):
    """
    获取最近的未解决告警记录（alarm_status为0或2），默认最多5条
    
    Args:
        db (Session): 数据库会话
        limit (int): 限制返回的记录数，默认为5
        
    Returns:
        tuple: (总数, 告警记录列表)
    """
    # 构建子查询，获取每个alarm_id的最新处理记录的处理时间
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
        CameraInfoDB.camera_name,
        ParkAreaDB.park_area,
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
    ).filter(
        AlarmDB.alarm_status.in_([0,2])  # 未解决的告警（处理中或未处理）
    ).order_by(
        AlarmDB.alarm_time.desc()  # 按告警时间倒序排列
    )

    return query.count(), query.limit(limit).all()