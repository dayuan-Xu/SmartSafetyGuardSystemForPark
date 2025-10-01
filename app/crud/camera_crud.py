from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session
from app.DB_models.camera_info_db import CameraInfoDB
from app.DB_models.park_area_db import ParkAreaDB
from app.JSON_schemas.camera_info_pydantic import CameraInfoCreate, CameraInfoUpdate


def get_camera_info(db: Session, camera_info_id: int) -> Optional[Tuple[CameraInfoDB, str]]:
    """
    根据ID获取摄像头信息，包含园区区域名称

    Args:
        db: 数据库会话
        camera_info_id: 摄像头信息ID

    Returns:
        Optional[Tuple[CameraInfoDB, str]]: 摄像头信息和园区区域名称的元组，或None
    """
    result = db.query(
        CameraInfoDB,
        ParkAreaDB.park_area
    ).outerjoin(
        ParkAreaDB, CameraInfoDB.park_area_id == ParkAreaDB.park_area_id
    ).filter(
        CameraInfoDB.camera_id == camera_info_id
    ).first()
    
    return result


def get_camera_infos_with_condition(
        db: Session,
        park_area_id: Optional[int] = None,
        analysis_mode: Optional[int] = None,
        camera_status: Optional[int] = None,
        skip: int = 0,
        limit: int = 10
):
    """
    根据条件获取摄像头信息列表（支持分页），包含园区区域信息

    Args:
        db: 数据库会话
        park_area_id: 园区区域ID
        analysis_mode: 分析模式
        camera_status: 摄像头状态
        skip: 跳过的记录数
        limit: 限制返回的记录数

    Returns:
        tuple: (总数, 摄像头信息列表)
    """
    # 构建联表查询
    query = db.query(
        CameraInfoDB,
        ParkAreaDB.park_area
    ).outerjoin(
        ParkAreaDB, CameraInfoDB.park_area_id == ParkAreaDB.park_area_id
    )

    # 添加园区区域ID条件
    if park_area_id is not None:
        query = query.filter(CameraInfoDB.park_area_id == park_area_id)

    # 添加分析模式条件
    if analysis_mode is not None:
        query = query.filter(CameraInfoDB.analysis_mode == analysis_mode)

    # 添加摄像头状态条件
    if camera_status is not None:
        query = query.filter(CameraInfoDB.camera_status == camera_status)

    # 返回计数和分页结果
    count = query.count()
    cameras_with_details = query.offset(skip).limit(limit).all()
    return count, cameras_with_details


def get_all_camera_infos(db: Session, skip: int = 0, limit: int = 100) -> List[CameraInfoDB]:
    """
    获取所有摄像头信息（支持分页）

    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 限制返回的记录数

    Returns:
        List[CameraInfoDB]: 摄像头信息列表
    """
    return db.query(CameraInfoDB).offset(skip).limit(limit).all()


# 3. 增：创建新摄像头信息
def create_camera_info(db: Session, camera_info: CameraInfoCreate) -> Tuple[CameraInfoDB, str]:
    # 1. 将 Pydantic 模型（CameraInfoCreate）转成 SQLAlchemy 模型（CameraInfoDB）
    db_camera_info = CameraInfoDB(**camera_info.model_dump())
    # 2. 提交到数据库
    db.add(db_camera_info)
    db.commit()
    db.refresh(db_camera_info)  # 刷新实例，获取数据库自动生成的 id 等字段
    
    # 3. 查询关联的园区区域名称
    park_area = db.query(ParkAreaDB.park_area).filter(
        ParkAreaDB.park_area_id == db_camera_info.park_area_id
    ).first()
    
    park_area_name = park_area.park_area if park_area else "未知区域"
    
    return db_camera_info, park_area_name

# 4. 改：根据 ID 修改摄像头信息
def update_camera_info(
    db: Session,
    camera_info_id: int,
    camera_info_update: CameraInfoUpdate
) -> Optional[Tuple[CameraInfoDB, str]]:
    # 先查询摄像头信息是否存在
    db_camera_info = db.query(CameraInfoDB).filter(
        CameraInfoDB.camera_id == camera_info_id
    ).first()
    
    if not db_camera_info:
        return None  # 摄像头信息不存在，返回 None
        
    # 将更新的字段赋值给数据库实例（只更新非 None 的字段）
    update_data = camera_info_update.model_dump(exclude_unset=True)  # 排除未传的字段
    for key, value in update_data.items():
        setattr(db_camera_info, key, value)
        
    # 更新时间字段
    db_camera_info.update_time = datetime.now()
    
    # 提交修改
    db.commit()
    db.refresh(db_camera_info)
    
    # 查询关联的园区区域名称
    park_area = db.query(ParkAreaDB.park_area).filter(
        ParkAreaDB.park_area_id == db_camera_info.park_area_id
    ).first()
    
    park_area_name = park_area.park_area if park_area else "未知区域"
    
    return db_camera_info, park_area_name

# 5. 批量删：根据 ID 列表批量删除摄像头信息
def delete_camera_infos(db: Session, camera_info_ids: List[int]) -> int:
    """
    批量删除摄像头信息

    Args:
        db: 数据库会话
        camera_info_ids: 摄像头信息ID列表

    Returns:
        int: 成功删除的记录数
    """
    # 查询存在的摄像头信息
    db_camera_infos = db.query(CameraInfoDB).filter(
        CameraInfoDB.camera_id.in_(camera_info_ids)
    ).all()

    # 获取实际存在的记录数量
    deleted_count = len(db_camera_infos)

    # 批量删除
    for db_camera_info in db_camera_infos:
        db.delete(db_camera_info)

    # 提交事务
    db.commit()

    return deleted_count