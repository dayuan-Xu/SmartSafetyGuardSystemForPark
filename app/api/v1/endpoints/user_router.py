from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.user_pydantic import UserResponse, UserCreate, UserUpdate, UserPageResult
from app.dependencies.db import get_db
from app.services.user_service import UserService

router = APIRouter()

# 1. GET /api/v1/users/{user_id}：获取单个用户信息  
@router.get("/{user_id}", response_model=Result[UserResponse], summary="获取单个用户信息", status_code=status.HTTP_200_OK)
async def read_user(
    user_id: Annotated[int, Path(title="用户ID", description="用户唯一标识")],
    db: Session = Depends(get_db)
):
    """
    根据用户ID获取单个用户信息

    Args:
        user_id (int): 用户唯一标识
        db (Session): 数据库会话

    Returns:
        Result[UserResponse]: 包含用户信息的统一响应结果
    """
    result = await UserService.get_user(db, user_id)
    return result

# 2. GET /api/v1/users：获取用户信息（支持条件分页）
@router.get("/", response_model=Result[UserPageResult], summary="获取用户信息（支持条件分页）", status_code=status.HTTP_200_OK)
async def get_users(
        skip: Annotated[int, Query(description="跳过的记录数")] = 0,
        limit: Annotated[int, Query(description="限制返回的记录数")] = 10,
        name: Annotated[Optional[str], Query(description="用户姓名")] = None,
        gender: Annotated[Optional[int], Query(description="用户性别: 0-女 1-男")] = None,
        start_time: Annotated[Optional[str], Query(description="入职时间左边界")] = None,
        end_time: Annotated[Optional[str], Query(description="入职时间右边界")] = None,
        db: Session = Depends(get_db)
):
    """
    获取用户信息（支持条件分页）

    Args:
        skip (int): 跳过的记录数
        limit (int): 限制返回的记录数
        name (Optional[str]): 用户姓名筛选条件
        gender (Optional[int]): 用户性别筛选条件
        start_time (Optional[str]): 入职时间左边界
        end_time (Optional[str]): 入职时间右边界
        db (Session): 数据库会话

    Returns:
        Result[UserPageResult]: 包含用户信息分页结果的统一响应
    """
    result = await UserService.get_users(db, skip=skip, limit=limit,
                                             name=name, gender=gender, 
                                             start_time=start_time, end_time=end_time)
    return result

# 3. POST /api/v1/users：创建新用户  
@router.post("/", response_model=Result[UserResponse], status_code=status.HTTP_201_CREATED, summary="创建新用户")
async def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    创建新用户

    Args:
        user (UserCreate): 用户创建信息
        db (Session): 数据库会话

    Returns:
        Result[UserResponse]: 包含新创建用户信息的统一响应结果
    """
    result = await UserService.create_user(db, user)
    return result

# 4. PUT /api/v1/users/{user_id}：修改用户信息  
@router.put("/{user_id}", response_model=Result[UserResponse], summary="修改用户信息", status_code=status.HTTP_200_OK)
async def update_existing_user(
    user_id: Annotated[int, Path(title="用户ID", description="用户唯一标识")],
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    根据用户ID修改用户信息

    Args:
        user_id (int): 用户唯一标识
        user_update (UserUpdate): 用户更新信息
        db (Session): 数据库会话

    Returns:
        Result[UserResponse]: 包含更新后用户信息的统一响应结果
    """
    result = await UserService.update_user(db, user_id, user_update)
    return result

# 5. DELETE /api/v1/users/{user_ids}：删除用户信息（支持单个或批量删除） 
@router.delete("/{user_ids}", response_model=Result, status_code=status.HTTP_200_OK, summary="删除用户信息（支持单个或批量删除）")
async def remove_user(
    user_ids: Annotated[str, Path(min_length=1, title="用户ID列表", description="用户ID列表，多个ID之间用英文逗号分隔")],
    db: Session = Depends(get_db)
):
    """
    删除用户信息（支持单个或批量删除）

    Args:
        user_ids (str): 用户ID列表，多个ID之间用英文逗号分隔
        db (Session): 数据库会话

    Returns:
        Result: 删除操作结果的统一响应
    """
    result = await UserService.delete_users(db, user_ids)
    return result