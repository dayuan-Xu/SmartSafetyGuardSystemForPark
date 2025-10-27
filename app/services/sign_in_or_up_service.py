import asyncio
from datetime import timedelta
from sqlalchemy.orm import Session
from app.config.app_settings import settings
from app.crud.user_crud import get_user_by_username, create_user
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.user_pydantic import UserRegister, UserCreate
from app.utils.jwt_utils import create_access_token
from app.utils.password_utils import verify_password, get_hashed_password
from app.services.thread_pool_manager import executor
from functools import partial


# 直接从settings获取访问令牌过期时间
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


class SignInOrUpService:
    @staticmethod
    async def login_for_access_token(form_data, db: Session) -> Result:
        """
        用户登录服务
        :param form_data: 登录表单数据
        :param db: 数据库会话
        :return: 登录结果
        """
        # 1. 检查用户是否存在
        db_user = await asyncio.get_event_loop().run_in_executor(
            executor, 
            partial(get_user_by_username, db, form_data.username)
        )
        if not db_user:
            return Result.ERROR("用户不存在")

        # 2. 验证密码
        password_valid = await asyncio.get_event_loop().run_in_executor(
            executor,
            partial(verify_password, form_data.password, db_user.password)
        )
        if not password_valid:
            return Result.ERROR("密码错误")

        # 3. 生成JWT令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await asyncio.get_event_loop().run_in_executor(
            executor,
            partial(create_access_token, data={"sub": db_user.user_name}, expires_delta=access_token_expires)
        )

        # 4. 返回成功响应
        return Result.SUCCESS({
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "user_id": db_user.user_id,
                "user_name": db_user.user_name,
                "name": db_user.name,
                "gender": db_user.gender,
                "user_role": db_user.user_role,
                "phone": db_user.phone,
                "create_time": db_user.create_time,
                "update_time": db_user.update_time
            }
        }, "登录成功")

    @staticmethod
    async def register_user(db: Session, user: UserRegister) -> Result:
        """
        用户注册服务
        :param db: 数据库会话
        :param user: 用户注册信息
        :return: 注册结果
        """
        # 1. 检查用户是否已存在
        existing_user = await asyncio.get_event_loop().run_in_executor(
            executor,
            partial(get_user_by_username, db, user.user_name)
        )
        if existing_user:
            return Result.ERROR("用户名已存在")

        # 2. 创建新用户
        hashed_password = await asyncio.get_event_loop().run_in_executor(
            executor,
            partial(get_hashed_password, user.password)
        )
        
        # 将UserRegister转换为UserCreate
        user_create_data = user.model_dump()
        # 如果name字段不存在，使用user_name作为默认name
        if 'name' not in user_create_data or not user_create_data['name']:
            user_create_data['name'] = user_create_data['user_name']
        user_create_data["password"] = hashed_password
        user_create = UserCreate(**user_create_data)
        
        try:
            db_user = await asyncio.get_event_loop().run_in_executor(
                executor,
                partial(create_user, db, user_create)
            )
            
            # 3. 生成JWT令牌
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = await asyncio.get_event_loop().run_in_executor(
                executor,
                partial(create_access_token, data={"sub": db_user.user_name}, expires_delta=access_token_expires)
            )

            # 4. 返回成功响应
            return Result.SUCCESS({
                "access_token": access_token,
                "token_type": "bearer",
                "user_info": {
                    "user_id": db_user.user_id,
                    "user_name": db_user.user_name,
                    "name": db_user.name,
                    "gender": db_user.gender,
                    "user_role": db_user.user_role,
                    "phone": db_user.phone,
                    "create_time": db_user.create_time,
                    "update_time": db_user.update_time
                }
            }, "注册成功")
        except Exception as e:
            return Result.ERROR(f"注册失败: {str(e)}")