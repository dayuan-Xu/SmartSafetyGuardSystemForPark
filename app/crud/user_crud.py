from sqlalchemy.orm import Session
from app.DB_models.user_db import UserDB  # 数据库模型
from app.JSON_schemas.user_pydantic import UserCreate, UserUpdate  # 请求模型
from typing import Optional, List

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

# 1. 查：根据 ID 获取单个用户信息
def get_user(db: Session, user_id: int) -> Optional[UserDB]:
    return db.query(UserDB).filter(UserDB.user_id == user_id).first()

# 2. 查：获取所有用户信息（支持分页，默认取 10 条）
def get_all_users(db: Session, skip: int = 0, limit: int = 10) -> List[UserDB]:
    return db.query(UserDB).offset(skip).limit(limit).all()

# 3. 增：创建新用户
def create_user(db: Session, user: UserCreate) -> UserDB:
    # 1. 将 Pydantic 模型（UserCreate）转成 SQLAlchemy 模型（UserDB）
    db_user = UserDB(**user.model_dump())
    # 2. 提交到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # 刷新实例，获取数据库自动生成的 id 等字段
    return db_user

# 4. 改：根据 ID 修改用户信息
def update_user(
    db: Session,
    user_id: int,
    user_update: UserUpdate
) -> Optional[UserDB]:
    # 先查询用户信息是否存在
    db_user = get_user(db, user_id)
    if not db_user:
        return None  # 用户信息不存在，返回 None
    # 将更新的字段赋值给数据库实例（只更新非 None 的字段）
    update_data = user_update.model_dump(exclude_unset=True)  # 排除未传的字段
    for key, value in update_data.rows():
        setattr(db_user, key, value)
    # 提交修改
    db.commit()
    db.refresh(db_user)
    return db_user

# 5. 批量删：根据 ID 列表批量删除用户信息
def delete_users(db: Session, user_ids: List[int]) -> int:
    """
    批量删除用户信息

    Args:
        db: 数据库会话
        user_ids: 用户信息ID列表

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


def get_user_by_username(db, username):
    """
    根据用户名查询用户信息

    Args:
        db: 数据库会话
        username: 用户名

    Returns:
        UserDB: 用户信息对象
    """
    return db.query(UserDB).filter(UserDB.username == username).first()
