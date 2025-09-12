from typing import List, Annotated
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.camera_info_pydantic import CameraInfoResponse, CameraInfoCreate, CameraInfoUpdate
from app.dependencies.db import get_db  # 获取数据库会话的依赖
from app.services.camera_info_service import CameraInfoService  # 导入service层代码负责业务逻辑

# 创建路由实例（tags 用于 API 文档分类）
router = APIRouter()

# 1. GET /api/v1/camera_infos/{camera_info_id}：获取单个摄像头信息
@router.get("/{camera_info_id}", response_model=Result[CameraInfoResponse], summary="获取单个摄像头信息")
def read_camera_info(
    camera_info_id: int,
    db: Session = Depends(get_db)
):
    return CameraInfoService.get_camera_info(db, camera_info_id)

# 2. GET /api/v1/camera_infos：获取所有摄像头信息（支持分页）
@router.get("/", response_model=Result[List[CameraInfoResponse]], summary="获取所有摄像头信息（支持分页）")
def read_all_camera_infos(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return CameraInfoService.get_all_camera_infos(db, skip=skip, limit=limit)

# 3. POST /api/v1/camera_infos：创建新摄像头信息
@router.post("/", response_model=Result[CameraInfoResponse], status_code=status.HTTP_201_CREATED, summary="创建新摄像头信息")
def create_new_camera_info(
    camera_info: CameraInfoCreate,
    db: Session = Depends(get_db)
):
    return CameraInfoService.create_camera_info(db, camera_info)

# 4. PUT /api/v1/camera_infos/{camera_info_id}：修改摄像头信息
@router.put("/{camera_info_id}", response_model=Result[CameraInfoResponse], summary="修改摄像头信息")
def update_existing_camera_info(
    camera_info_id: int,
    camera_info_update: CameraInfoUpdate,
    db: Session = Depends(get_db)
):
    return CameraInfoService.update_camera_info(db, camera_info_id, camera_info_update)

# 5. DELETE /api/v1/camera_infos/{camera_info_ids}：删除摄像头信息（支持单个或批量删除）
@router.delete("/{camera_info_ids}", response_model=Result, status_code=status.HTTP_200_OK, summary="删除摄像头信息（支持单个或批量删除）")
def remove_camera_info(
    camera_info_ids: Annotated[str, Path(min_length=1, title="摄像头信息ID列表", description="摄像头信息ID列表，多个ID之间用英文逗号分隔")],
    db: Session = Depends(get_db)
):
    return CameraInfoService.delete_camera_infos(db, camera_info_ids)
