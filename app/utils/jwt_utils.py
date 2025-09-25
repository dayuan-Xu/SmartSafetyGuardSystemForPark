from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
import jwt
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.config.security_config import SECRET_KEY, ALGORITHM
from app.dependencies.db import get_db


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        str: 编码后的JWT令牌
    """
    to_encode = data.copy()  # 保存原始的用户关键信息(明文)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})  # 添加过期时间（合并两个dict）
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # 生成jwt：输入payload和密钥，利用指定的签名算法生成签名，
    # JWT最终结构：签名算法信息的base64编码（也叫Header）、用户数据的base64编码（也叫Payload）、生成的签名的base64编码（也叫Signature）
    return encoded_jwt


def verify_token(token):
    """
    验证jwt并获取当前登录用户的信息（比如用户名）

    Args:
        db: 数据库会话
        token: JWT令牌

    Returns:
        logged_user_info: 当前登录用户的信息

    Raises:
        HTTPException: 当令牌无效或用户不存在时
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials jwt令牌解析出现错误",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logged_user_info = payload.get("sub")
        if logged_user_info is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return logged_user_info


