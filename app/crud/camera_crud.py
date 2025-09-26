from sqlalchemy.orm import Session
from app.DB_models.camera_info_db import CameraInfoDB  # 数据库模型
from app.JSON_schemas.camera_info_pydantic import CameraInfoCreate, CameraInfoUpdate  # 请求模型
from typing import Optional, List
"""
CameraInfoDB 模型的含义:
    类级别代表整张表
        CameraInfoDB 类代表整个 camera_info 数据库表
        它定义了表的结构（列名、数据类型、约束等）
        是操作该表的入口点
    实例代表单条记录
        CameraInfoDB 的实例代表表中的一行记录
        每个实例都有具体的属性值
"""

# 1. 查：根据 ID 获取单个 摄像头信息
def get_camera_info(db: Session, camera_id: int) -> Optional[CameraInfoDB]:
    return db.query(CameraInfoDB).filter(CameraInfoDB.camera_id == camera_id).first()

# 2.1. 查：获取所有摄像头信息（支持分页，默认取 10 条）
def get_all_camera_infos(db: Session, skip: int = 0, limit: int = 10) -> List[CameraInfoDB]:
    return db.query(CameraInfoDB).offset(skip).limit(limit).all()


# 2.2. 查：根据条件获取摄像头信息（支持分页）
def get_camera_infos_with_condition(
        db: Session,
        park_area: Optional[str] = None,
        analysis_mode: Optional[int] = None,
        camera_status: Optional[int] = None,
        skip: int = 0,
        limit: int = 10
) -> List[CameraInfoDB]:
    query = db.query(CameraInfoDB)

    # 添加园区位置条件
    if park_area:
        query = query.filter(CameraInfoDB.park_area == park_area)

    # 添加分析模式条件
    if analysis_mode is not None:
        query = query.filter(CameraInfoDB.analysis_mode == analysis_mode)

    # 添加摄像头状态条件
    if camera_status is not None:
        query = query.filter(CameraInfoDB.camera_status == camera_status)

    return query.offset(skip).limit(limit).all()
# 3. 增：创建新摄像头信息
def create_camera_info(db: Session, camera_info: CameraInfoCreate) -> CameraInfoDB:
    # 1. 将 Pydantic 模型（CameraInfoCreate）转成 SQLAlchemy 模型（CameraInfoDB）
    db_camera_info = CameraInfoDB(** camera_info.model_dump())
    # 2. 提交到数据库
    db.add(db_camera_info)
    db.commit()
    db.refresh(db_camera_info)  # 刷新实例，获取数据库自动生成的 id 等字段
    return db_camera_info

# 4. 改：根据 ID 修改摄像头信息
def update_camera_info(
    db: Session,
    camera_info_id: int,
    camera_info_update: CameraInfoUpdate
) -> Optional[CameraInfoDB]:
    # 先查询摄像头信息是否存在
    db_camera_info = get_camera_info(db, camera_info_id)
    if not db_camera_info:
        return None  # 摄像头信息不存在，返回 None
    # 将更新的字段赋值给数据库实例（只更新非 None 的字段）
    update_data = camera_info_update.model_dump(exclude_unset=True)  # 排除未传的字段
    for key, value in update_data.rows():
        setattr(db_camera_info, key, value)
    # 提交修改
    db.commit()
    db.refresh(db_camera_info)
    return db_camera_info

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


