import asyncio
from datetime import timedelta
from typing import Union

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError as SQLIntegrityError
from sqlalchemy.orm import Session

from app.DB_models.user_db import UserDB
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.security_pydantic import Token
from app.JSON_schemas.user_pydantic import UserCreate, UserRegister
from app.config.security_config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.crud.user_crud import get_user_by_username, create_user
from app.services.thread_pool_manager import executor as db_executor
from app.utils.jwt_utils import create_access_token
from app.utils.logger import get_logger
from app.utils.password_utils import verify_password, get_password_hash

logger=get_logger()

class SignInOrUpService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Union[UserDB, bool]:
        """
        验证用户密码是否和数据库种的哈希化密码一致

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码

        Returns:
            UserInDB | bool: 用户对象或False
        """
        # 从数据库获取用户
        db_user = get_user_by_username(db, username)
        if not db_user:
            return False

        # 验证密码
        hashed_password = db_user.password
        if not verify_password(password, hashed_password):
            return False

        return db_user

    @staticmethod
    async def register_user(db: Session, user: UserRegister) -> Result:
        """
        用户注册功能

        Args:
            db (Session): 数据库会话
            user (UserRegister): 用户注册请求模型

        Returns:
            Result: 包含新注册用户信息或错误信息的统一响应
        """
        try:
            def _register_user():
                # 检查用户名是否已存在
                existing_user = get_user_by_username(db, user.user_name)
                if existing_user:
                    return Result.ERROR(msg=f"用户名已存在: Username '{user.user_name}' already exists")

                # 对密码进行哈希处理
                user_data = user.model_dump()
                user_data['password'] = get_password_hash(user.password)

                # 补全相较于UserCreate缺少的字段
                user_data.update({'name':'待定', 'gender': 1, 'user_role': 0, 'phone': user.phone})

                # 创建该用户
                userDB = create_user(db, UserCreate(**user_data))

                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={"sub": userDB.user_name}, expires_delta=access_token_expires
                )
                token_data = Token(access_token=access_token, token_type="bearer")
                result = Result.SUCCESS(data=token_data, msg="注册成功")
                return result

            # 使用线程池执行数据库操作
            return await asyncio.get_event_loop().run_in_executor(db_executor, _register_user)
        except  SQLIntegrityError as e:
            logger.error(f"用户注册失败: {str(e)}")
            error_msg = str(e).lower()
            if "duplicate entry" in error_msg:
                return Result.ERROR(msg="注册失败，请更换用户名或手机号")
        except Exception as e:
            logger.error(f"用户注册失败: {str(e)}")
            return Result.ERROR(msg=f"注册失败: {str(e)}")


    @staticmethod
    async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm,
        db: Session
    ) -> Result[Token]:
        """
        用户登录获取访问令牌

        Args:
            form_data: OAuth2表单数据（用户名和密码）
            db: 数据库会话

        Returns:
            Result[Token]: 包含访问令牌或错误信息的统一响应
        """
        try:
            db_user = SignInOrUpService.authenticate_user(db, form_data.username, form_data.password)
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": db_user.user_name}, expires_delta=access_token_expires
            )
            token_data = Token(access_token=access_token, token_type="bearer")
            result = Result.SUCCESS(data=token_data, msg="登录成功")
            return result
        except HTTPException as e:
            result = Result.ERROR(msg=e.detail)
            return result
        except Exception as e:
            result = Result.ERROR(msg=f"登录失败: {str(e)}")
            return result