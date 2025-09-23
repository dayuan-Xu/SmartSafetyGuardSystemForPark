from datetime import timedelta
from typing import Union
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.security_pydantic import Token, User, UserInDB
from app.config.security_config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.crud.user_crud import get_user_by_username
from app.utils.password_utils import verify_password
from app.utils.jwt_utils import create_access_token



class LoginAndSelfService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Union[UserInDB, bool]:
        """
        验证用户凭据

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
        if not verify_password(password, db_user.hashed_password):
            return False

        # 创建 UserInDB 对象返回
        user_in_db = UserInDB(
            username=db_user.user_name,
            email=db_user.email,
            full_name=db_user.full_name,
            disabled=db_user.disabled,
            hashed_password=db_user.hashed_password
        )

        return user_in_db

    """
    安全认证业务逻辑处理类
    """

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
            user = LoginAndSelfService.authenticate_user(db, form_data.username, form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
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

    @staticmethod
    def get_current_user_info(current_user: User) -> Result[User]:
        """
        获取当前用户信息

        Args:
            current_user: 当前用户（已通过路由依赖验证）

        Returns:
            Result[User]: 包含用户信息或错误信息的统一响应
        """
        # 由于在路由层已经完成用户认证，这里直接返回用户信息即可
        return Result.SUCCESS(data=current_user, msg="获取用户信息成功")

    @staticmethod
    def get_current_user_items(current_user: User) -> Result:
        """
        获取当前用户拥有的项目

        Args:
            current_user: 当前用户（已通过路由依赖验证）

        Returns:
            Result: 包含用户项目列表或错误信息的统一响应
        """
        # 由于在路由层已经完成用户认证，这里直接构造并返回用户项目即可
        items = [{"item_id": "Foo", "owner": current_user.username}]
        return Result.SUCCESS(data=items, msg="获取用户项目成功")