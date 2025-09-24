from typing import List, Annotated

from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session

from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.user_pydantic import UserResponse, UserCreate, UserUpdate, UserPageResult
from app.dependencies.db import get_db
from app.services.user_service import UserService

router = APIRouter()

# 1. GET /api/v1/users/{user_id}：获取单个用户信息 (需要认证)
@router.get("/{user_id}", response_model=Result[UserResponse], summary="获取单个用户信息")
async def read_user(
    user_id: int,
        db: Session = Depends(get_db)
):
    result = await UserService.get_user(db, user_id)
    return result

# 2. GET /api/v1/users：获取所有用户信息（支持分页）(需要认证)
@router.get("/", response_model=Result[UserPageResult], summary="获取所有用户信息（支持分页）")
async def read_all_users(
        skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    result = await UserService.get_all_users(db, skip=skip, limit=limit)
    return result

# 3. POST /api/v1/users：创建新用户 (需要认证)
@router.post("/", response_model=Result[UserResponse], status_code=status.HTTP_201_CREATED, summary="创建新用户")
async def create_new_user(
    user: UserCreate,
        db: Session = Depends(get_db)
):
    result = await UserService.create_user(db, user)
    return result

# 4. PUT /api/v1/users/{user_id}：修改用户信息 (需要认证)
@router.put("/{user_id}", response_model=Result[UserResponse], summary="修改用户信息")
async def update_existing_user(
    user_id: int,
    user_update: UserUpdate,
        db: Session = Depends(get_db)
):
    result = await UserService.update_user(db, user_id, user_update)
    return result

# 5. DELETE /api/v1/users/{user_ids}：删除用户信息（支持单个或批量删除）(需要认证)
@router.delete("/{user_ids}", response_model=Result, status_code=status.HTTP_200_OK, summary="删除用户信息（支持单个或批量删除）")
async def remove_user(
    user_ids: Annotated[str, Path(min_length=1, title="用户ID列表", description="用户ID列表，多个ID之间用英文逗号分隔")],
        db: Session = Depends(get_db)
):
    result = await UserService.delete_users(db, user_ids)
    return result