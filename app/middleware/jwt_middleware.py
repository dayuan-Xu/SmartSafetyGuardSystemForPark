from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import jwt
from sqlalchemy.orm import Session
from typing import Optional
import re

from app.config.security_config import SECRET_KEY, ALGORITHM
from app.dependencies.db import get_db
from app.crud.user_crud import get_user_by_username
from app.JSON_schemas.security_pydantic import User


class JWTMiddleware:
    """
    JWT验证中间件
    实现类似Spring Boot拦截器的功能，对需要认证的请求进行JWT验证
    """

    def __init__(self, excluded_paths: Optional[list] = None):
        """
        初始化JWT中间件

        Args:
            excluded_paths: 不需要验证的路径列表，支持正则表达式
        """
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/",
            "/token"
        ]

    def is_path_excluded(self, path: str) -> bool:
        """
        检查路径是否在排除列表中

        Args:
            path: 请求路径

        Returns:
            bool: 是否排除
        """
        for excluded_path in self.excluded_paths:
            # 支持正则表达式匹配
            if re.match(excluded_path, path):
                return True
            # 支持精确匹配
            if path == excluded_path:
                return True
        return False

    async def authenticate(self, request: Request) -> Optional[User]:
        """
        验证JWT令牌并获取用户信息

        Args:
            request: 请求对象

        Returns:
            User: 用户信息，如果验证失败则返回None

        Raises:
            HTTPException: 当令牌无效或用户不存在时
        """
        # 获取Authorization头
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 检查Bearer令牌格式
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 提取令牌
        token = auth_header.split(" ")[1]

        # 解码JWT令牌
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 获取数据库会话并查询用户
        db_gen = get_db()
        db: Session = next(db_gen)
        try:
            db_user = get_user_by_username(db, username)
            if db_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 检查用户是否被禁用
            if db_user.disabled:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user",
                )

            # 创建User对象
            user = User(
                username=db_user.user_name,
                email=db_user.email,
                full_name=db_user.full_name,
                disabled=db_user.disabled
            )
            return user
        finally:
            # 确保数据库会话被正确关闭
            try:
                next(db_gen)
            except StopIteration:
                pass  # 正常情况，生成器已结束

    async def __call__(self, request: Request, call_next):
        """
        中间件主处理函数

        Args:
            request: 请求对象
            call_next: 下一个处理函数

        Returns:
            Response: 响应对象
        """
        # 检查是否需要跳过验证
        if self.is_path_excluded(request.url.path):
            return await call_next(request)

        try:
            # 验证JWT令牌
            user = await self.authenticate(request)
            # 将用户信息添加到请求状态中，供后续处理使用
            request.state.user = user
        except HTTPException as e:
            # JWT验证失败，返回错误响应
            return JSONResponse(
                status_code=e.status_code,
                content={"code": 0, "msg": e.detail, "data": None}
            )

        # 继续处理请求
        response = await call_next(request)
        return response