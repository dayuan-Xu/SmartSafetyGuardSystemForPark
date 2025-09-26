from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.security_pydantic import Token
from app.JSON_schemas.user_pydantic import UserRegister
from app.dependencies.db import get_db
from app.services.sign_in_or_up_service import SignInOrUpService

router = APIRouter()

@router.post("/token", response_model=Result[Token], summary="用户登录认证", status_code=status.HTTP_200_OK, tags=["注册登录"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    """
    用户登录接口，验证用户名和密码，返回访问令牌

    Args:
        form_data (OAuth2PasswordRequestForm): 登录表单数据，包含用户名和密码
        db (Session): 数据库会话

    Returns:
        Result[Token]: 包含访问令牌的统一响应结果
    """
    result = await SignInOrUpService.login_for_access_token(form_data, db)
    return result


@router.post("/register", response_model=Result[Token], status_code=status.HTTP_201_CREATED, summary="用户注册", tags=["注册登录"])
async def register(user: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册接口，用于新用户注册账户

    Args:
        user (UserRegister): 用户注册信息
        db (Session): 数据库会话

    Returns:
        Result[Token]: 包含访问令牌的统一响应结果
    """
    result = await SignInOrUpService.register_user(db, user)
    return result