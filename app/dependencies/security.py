from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from app.JSON_schemas.security_pydantic import TokenData, User
from app.config.security_config import SECRET_KEY, ALGORITHM
from app.crud.user_crud import get_user_by_username as crud_get_user_by_username
from app.dependencies.db import get_db

# 创建了一个 OAuth2 密码流的认证方案，本质上是一个特殊函数对象
# 使用它进行依赖注入时，它能告诉 FastAPI 这个接口需要 Bearer Token 认证
# 当请求到达时，FastAPI 会调用该对象自动从请求头中提取 Authorization: Bearer <token> 字段
# 提取出的 token 字符串会被返回
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    """
    获取当前用户
    
    Args:
        db: 数据库会话
        token: JWT令牌
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 当令牌无效或用户不存在时
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
    # 从数据库获取用户
    db_user = crud_get_user_by_username(db, token_data.username)
    if db_user is None:
        raise credentials_exception
    
    return User(
        username=db_user.user_name,
        email=db_user.email,
        full_name=db_user.full_name,
        disabled=db_user.disabled
    )


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 当前活跃用户
        
    Raises:
        HTTPException: 当用户被禁用时
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user