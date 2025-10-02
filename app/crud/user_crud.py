from sqlalchemy.orm import Session
from app.DB_models.user_db import UserDB  # 数据库模型
from app.JSON_schemas.user_pydantic import UserCreate, UserUpdate  # 请求模型
from typing import Optional, List

from app.utils.password_utils import get_password_hash

"""
UserDB 模型的含义:
    类级别代表整张表
        UserDB 类代表整个 user 数据库表
        它定义了表的结构（列名、数据类型、约束等）
        是操作该表的入口点
    实例代表单条记录
        UserDB 的实例代表表中的一行记录
        每个实例都有具体的属性值
"""

def get_user(db: Session, user_id: int) -> Optional[UserDB]:
    """
    根据 ID 获取单个用户信息

    Args:
        db (Session): 数据库会话
        user_id (int): 用户ID

    Returns:
        Optional[UserDB]: 用户信息对象或None
    """
    return db.query(UserDB).filter(UserDB.user_id == user_id).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 10, 
                 name: str = None, gender: int = None,
                 start_time: str = None, end_time: str = None) -> List[UserDB]:
    """
    获取所有用户信息（支持分页和筛选）

    Args:
        db (Session): 数据库会话
        skip (int): 跳过的记录数，默认为0
        limit (int): 限制返回的记录数，默认为10
        name (str): 用户姓名（模糊查询）
        gender (int): 用户性别
        start_time (str): 入职时间起始时间
        end_time (str): 入职时间结束时间

    Returns:
        List[UserDB]: 用户信息列表
    """
    query = db.query(UserDB)
    
    # 根据姓名筛选
    if name:
        query = query.filter(UserDB.name.like(f"%{name}%"))
    
    # 根据性别筛选
    if gender is not None:
        query = query.filter(UserDB.gender == gender)
    
    # 根据入职时间范围筛选
    if start_time:
        query = query.filter(UserDB.create_time >= start_time)
    
    if end_time:
        query = query.filter(UserDB.create_time <= end_time)
    
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> UserDB:
    """
    创建新用户

    Args:
        db (Session): 数据库会话
        user (UserCreate): 用户创建信息

    Returns:
        UserDB: 新创建的用户对象
    """
    # 1. 将 Pydantic 模型（UserCreate）转成 SQLAlchemy 模型（UserDB）
    if user.password:
        user.password = get_password_hash(user.password)
    db_user = UserDB(**user.model_dump())
    # 2. 提交到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # 刷新实例，获取数据库自动生成的 id 等字段
    return db_user

def update_user(
    db: Session,
    user_id: int,
    user_update: UserUpdate
) -> Optional[UserDB]:
    """
    根据 ID 修改用户信息

    Args:
        db (Session): 数据库会话
        user_id (int): 用户ID
        user_update (UserUpdate): 用户更新信息

    Returns:
        Optional[UserDB]: 更新后的用户信息对象或None（如果未找到）
    """
    # 先查询用户信息是否存在
    db_user = get_user(db, user_id)
    if not db_user:
        return None  # 用户信息不存在，返回 None
    # 将更新的字段赋值给数据库实例（只更新非 None 的字段）
    update_data = user_update.model_dump(exclude_unset=True)  # 排除未传的字段
    # 明文密码哈希化
    if update_data.get("password"):
        update_data["password"] = get_password_hash(update_data["password"])
    for key, value in update_data.items():
        setattr(db_user, key, value)
    # 提交修改
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_users(db: Session, user_ids: List[int]) -> int:
    """
    批量删除用户信息

    Args:
        db (Session): 数据库会话
        user_ids (List[int]): 用户信息ID列表

    Returns:
        int: 成功删除的记录数
    """
    # 查询存在的用户信息
    db_users = db.query(UserDB).filter(
        UserDB.user_id.in_(user_ids)
    ).all()

    # 获取实际存在的记录数量
    deleted_count = len(db_users)

    # 批量删除
    for db_user in db_users:
        db.delete(db_user)

    # 提交事务
    db.commit()

    return deleted_count


def get_user_by_username(db: Session, username: str) -> Optional[UserDB]:
    """
    根据用户名查询用户信息

    Args:
        db (Session): 数据库会话
        username (str): 用户名

    Returns:
        Optional[UserDB]: 用户信息对象或None
    """
    return db.query(UserDB).filter(UserDB.user_name == username).first()