import asyncio
from typing import List
from sqlalchemy.orm import Session

from app.DB_models.user_db import UserDB
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.user_pydantic import UserResponse, UserCreate, UserUpdate
from app.crud.user_crud import (
    get_user as crud_get_user,
    get_all_users as crud_get_all_users,
    create_user as crud_create_user,
    update_user as crud_update_user,
    delete_users as crud_delete_users
)
from app.services.thread_pool_manager import executor as db_executor


class UserService:
    """
    用户信息业务逻辑处理类
    """

    @staticmethod
    async def get_user(db: Session, user_id: int) -> Result[UserResponse]:
        """
        获取单个用户信息

        Args:
            db (Session): 数据库会话
            user_id (int): 用户ID

        Returns:
            Result[UserResponse]: 包含用户信息或错误信息的统一响应
        """
        # 使用线程池执行数据库操作
        db_user = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_get_user, db, user_id
        )
        if not db_user:
            return Result.ERROR(msg=f"用户信息未找到: User with id {user_id} not found")
        return Result.SUCCESS(data=db_user, msg="获取用户信息成功")

    @staticmethod
    async def get_all_users(db: Session, skip: int = 0, limit: int = 10) -> Result[List[UserResponse]]:
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
            # 使用线程池执行数据库操作
            users = await asyncio.get_event_loop().run_in_executor(
                db_executor, crud_get_all_users, db, skip, limit
            )
            return Result.SUCCESS(data=users, msg="获取用户列表成功")
        except Exception as e:
            return Result.ERROR(msg="获取用户列表失败")

    @staticmethod
    async def create_user(db: Session, user_create: UserCreate) -> Result[UserResponse]:
        """
        创建新用户

        Args:
            db (Session): 数据库会话
            user_create (UserCreate): 用户创建请求模型

        Returns:
            Result[UserResponse]: 包含新创建用户信息或错误信息的统一响应
        """
        try:
            def _create_user():
                # 检查用户名是否已存在
                existing_user = db.query(UserDB).filter(UserDB.user_name == user_create.user_name).first()
                if existing_user:
                    return Result.ERROR(msg=f"用户名已存在: Username '{user_create.user_name}' already exists")

                # 创建新用户对象
                created_user = crud_create_user(db, user_create)
                return Result.SUCCESS(data=created_user, msg="用户创建成功")
            
            # 使用线程池执行数据库操作
            return await asyncio.get_event_loop().run_in_executor(db_executor, _create_user)
        except Exception as e:
            return Result.ERROR(msg="创建用户失败")

    @staticmethod
    async def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Result[UserResponse]:
        """
        修改用户信息

        Args:
            db (Session): 数据库会话
            user_id (int): 用户ID
            user_update (UserUpdate): 用户更新请求模型

        Returns:
            Result[UserResponse]: 包含更新后用户信息或错误信息的统一响应
        """
        # 使用线程池执行数据库操作
        db_user = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_update_user, db, user_id, user_update
        )
        if not db_user:
            return Result.ERROR(msg=f"用户信息未找到: User with id {user_id} not found")
        return Result.SUCCESS(data=db_user, msg="用户信息更新成功")

    @staticmethod
    async def delete_users(db: Session, user_ids_str: str) -> Result:
        """
        删除用户信息（支持单个或批量删除）

        Args:
            db (Session): 数据库会话
            user_ids_str (str): 用户ID字符串，多个ID之间用英文逗号分隔

        Returns:
            Result: 包含操作结果或错误信息的统一响应
        """
        # 解析用户ID列表
        try:
            user_ids = [int(id.strip()) for id in user_ids_str.split(',') if id.strip().isdigit()]
            if not user_ids:
                return Result.ERROR(msg="无效的用户ID列表")
        except ValueError:
            return Result.ERROR("ID参数格式错误，请提供有效的数字ID")

        # 使用线程池执行数据库操作
        deleted_count = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_delete_users, db, user_ids
        )

        # 构造并返回响应结果
        if deleted_count == 0:
            return Result.ERROR("删除失败: 没有找到指定的任意一个用户信息")
        elif deleted_count < len(user_ids):
            return Result.SUCCESS(
                {"deleted_count": deleted_count},
                f"部分删除成功: 成功删除{deleted_count}条记录"
            )
        else:
            return Result.SUCCESS(
                {"deleted_count": deleted_count},
                f"批量删除成功: 共删除{deleted_count}条记录"
            )