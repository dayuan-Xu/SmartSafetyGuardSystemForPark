from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.DB_models.user_db import UserDB
from app.JSON_schemas.user_pydantic import UserResponse, UserCreate, UserUpdate
from app.JSON_schemas.Result_pydantic import Result
import logging

# 配置日志
logger = logging.getLogger(__name__)

class UserService:
    """
    用户信息业务逻辑处理类
    """

    @staticmethod
    def get_user(db: Session, user_id: int) -> Result[UserResponse]:
        """
        获取单个用户信息

        Args:
            db (Session): 数据库会话
            user_id (int): 用户ID

        Returns:
            Result[UserResponse]: 包含用户信息或错误信息的统一响应
        """
        try:
            user = db.query(UserDB).filter(UserDB.user_id == user_id).first()
            if user:
                return Result.SUCCESS(data=user, msg="获取用户信息成功")
            else:
                return Result.ERROR(msg=f"用户信息未找到: User with id {user_id} not found")
        except SQLAlchemyError as e:
            logger.error(f"数据库查询错误: {e}")
            return Result.ERROR(msg="数据库查询失败")
        except Exception as e:
            logger.error(f"获取用户信息时发生未知错误: {e}")
            return Result.ERROR(msg="获取用户信息失败")

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 10) -> Result[List[UserResponse]]:
        """
        获取所有用户信息（支持分页）

        Args:
            db (Session): 数据库会话
            skip (int): 跳过的记录数
            limit (int): 每页的记录数

        Returns:
            Result[List[UserResponse]]: 包含用户信息列表或错误信息的统一响应
        """
        try:
            users = db.query(UserDB).offset(skip).limit(limit).all()
            return Result.SUCCESS(data=users, msg="获取用户列表成功")
        except SQLAlchemyError as e:
            logger.error(f"数据库查询错误: {e}")
            return Result.ERROR(msg="数据库查询失败")
        except Exception as e:
            logger.error(f"获取用户列表时发生未知错误: {e}")
            return Result.ERROR(msg="获取用户列表失败")

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> Result[UserResponse]:
        """
        创建新用户

        Args:
            db (Session): 数据库会话
            user_create (UserCreate): 用户创建请求模型

        Returns:
            Result[UserResponse]: 包含新创建用户信息或错误信息的统一响应
        """
        try:
            # 检查用户名是否已存在
            existing_user = db.query(UserDB).filter(UserDB.user_name == user_create.user_name).first()
            if existing_user:
                return Result.ERROR(msg=f"用户名已存在: Username '{user_create.user_name}' already exists")

            # 创建新用户对象
            db_user = UserDB(**user_create.dict())
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return Result.SUCCESS(data=db_user, msg="用户创建成功")
        except SQLAlchemyError as e:
            logger.error(f"数据库操作错误: {e}")
            db.rollback()
            return Result.ERROR(msg="数据库操作失败")
        except Exception as e:
            logger.error(f"创建用户时发生未知错误: {e}")
            db.rollback()
            return Result.ERROR(msg="创建用户失败")

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Result[UserResponse]:
        """
        修改用户信息

        Args:
            db (Session): 数据库会话
            user_id (int): 用户ID
            user_update (UserUpdate): 用户更新请求模型

        Returns:
            Result[UserResponse]: 包含更新后用户信息或错误信息的统一响应
        """
        try:
            # 查找要更新的用户
            db_user = db.query(UserDB).filter(UserDB.user_id == user_id).first()
            if not db_user:
                return Result.ERROR(msg=f"用户信息未找到: User with id {user_id} not found")

            # 更新用户信息
            update_data = user_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_user, key, value)

            db.commit()
            db.refresh(db_user)
            return Result.SUCCESS(data=db_user, msg="用户信息更新成功")
        except SQLAlchemyError as e:
            logger.error(f"数据库操作错误: {e}")
            db.rollback()
            return Result.ERROR(msg="数据库操作失败")
        except Exception as e:
            logger.error(f"更新用户信息时发生未知错误: {e}")
            db.rollback()
            return Result.ERROR(msg="更新用户信息失败")

    @staticmethod
    def delete_users(db: Session, user_ids_str: str) -> Result:
        """
        删除用户信息（支持单个或批量删除）

        Args:
            db (Session): 数据库会话
            user_ids_str (str): 用户ID字符串，多个ID之间用英文逗号分隔

        Returns:
            Result: 包含操作结果或错误信息的统一响应
        """
        try:
            # 解析用户ID列表
            user_ids = [int(id.strip()) for id in user_ids_str.split(',') if id.strip().isdigit()]
            if not user_ids:
                return Result.ERROR(msg="无效的用户ID列表")
        except ValueError:
            return Result.ERROR("ID参数格式错误，请提供有效的数字ID")

            # 查找要删除的用户
            users_to_delete = db.query(UserDB).filter(UserDB.user_id.in_(user_ids)).all()
            if not users_to_delete:
                return Result.ERROR(msg="未找到指定的用户")

            # 删除用户
            deleted_count = 0
            for user in users_to_delete:
                db.delete(user)
                deleted_count += 1

            db.commit()
            return Result.SUCCESS(data=None, msg=f"成功删除 {deleted_count} 个用户")
        except ValueError:
            return Result.ERROR(msg="用户ID格式错误")
        except SQLAlchemyError as e:
            logger.error(f"数据库操作错误: {e}")
            db.rollback()
            return Result.ERROR(msg="数据库操作失败")
        except Exception as e:
            logger.error(f"删除用户时发生未知错误: {e}")
            db.rollback()
            return Result.ERROR(msg="删除用户失败")