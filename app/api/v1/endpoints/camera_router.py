from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.camera_info_pydantic import CameraInfoResponse, CameraInfoCreate, CameraInfoUpdate
from app.dependencies.db import get_db  # 获取数据库会话的依赖
from app.services.camera_info_service import CameraInfoService # 导入service层代码负责业务逻辑
from app.crud.camera_crud import (
    get_camera_info, get_all_camera_infos, create_camera_info, update_camera_info
)


# 创建路由实例（tags 用于 API 文档分类）
# 这个 router 实例的作用是：
# 收集接口：把当前文件中定义的所有接口（如获取摄像头信息、创建摄像头信息等）收集到一起
# 统一管理：为这些接口添加统一的标签（tags=["摄像头信息"]），方便在 API 文档中分类显示
# 便于注册：作为一个整体，可以被 main.py 一次性注册到主应用中

router = APIRouter()

# 1. GET /api/v1/camera_infos/{camera_info_id}：获取单个摄像头信息
@router.get("/{camera_info_id}", response_model=Result[CameraInfoResponse],summary="获取单个摄像头信息")
def read_camera_info(
    camera_info_id: int,
    db: Session = Depends(get_db)  # 依赖注入：自动获取数据库会话
):
    db_camera_info = get_camera_info(db, camera_info_id)
    if not db_camera_info:
        return Result.ERROR(f"CameraInfo not found with given id={camera_info_id}")
    return Result.SUCCESS(db_camera_info) # 自动转成 Result[CameraInfoResponse] 格式返回

# 2. GET /api/v1/camera_infos：获取所有摄像头信息（支持分页）
@router.get("/", response_model=Result[List[CameraInfoResponse]],summary="获取所有摄像头信息（支持分页）")
def read_all_camera_infos(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    camera_infos = get_all_camera_infos(db, skip=skip, limit=limit)
    return Result.SUCCESS(camera_infos)  # 封装为 Result 格式


# 3. POST /api/v1/camera_infos：创建新摄像头信息
@router.post("/", response_model=Result[CameraInfoResponse], status_code=status.HTTP_201_CREATED,summary="创建新摄像头信息")
def create_new_camera_info(
    camera_info: CameraInfoCreate,
    db: Session = Depends(get_db)
):
    created_camera = create_camera_info(db, camera_info)
    return Result.SUCCESS(created_camera)  # 封装为 Result 格式


# 4. PUT /api/v1/camera_infos/{camera_info_id}：修改摄像头信息
@router.put("/{camera_info_id}", response_model=Result[CameraInfoResponse],summary="修改摄像头信息")
def update_existing_camera_info(
    camera_info_id: int,
    camera_info_update: CameraInfoUpdate,
    db: Session = Depends(get_db)
):
    db_camera_info = update_camera_info(db, camera_info_id, camera_info_update)
    if not db_camera_info:
        return Result.ERROR(f"Update failure: CameraInfo not found with given id={camera_info_id}")
    return Result.SUCCESS(db_camera_info)  # 封装为 Result 格式


# 5. DELETE /api/v1/camera_infos/{camera_info_ids}：删除摄像头信息（支持单个或批量删除）
@router.delete("/{camera_info_ids}", response_model=Result, status_code=status.HTTP_200_OK, summary="删除摄像头信息（支持单个或批量删除）")
def remove_camera_info(
    camera_info_ids: str,
    db: Session = Depends(get_db)
):
    return CameraInfoService.delete_camera_infos(db, camera_info_ids)
