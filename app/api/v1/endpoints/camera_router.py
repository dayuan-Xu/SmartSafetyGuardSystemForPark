from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.camera_info_pydantic import CameraInfoResponse, CameraInfoCreate, CameraInfoUpdate,CameraInfoPageResponse
from app.dependencies.db import get_db  # 获取数据库会话的依赖
from app.services.camera_info_service import CameraInfoService  # 导入service层代码负责业务逻辑

# 创建路由实例（tags 用于 API 文档分类）
router = APIRouter()

# 1.1. GET /api/v1/camera_infos/{camera_info_id}：获取单个摄像头信息
@router.get("/{camera_info_id}", response_model=Result[CameraInfoResponse], summary="获取单个摄像头信息")
def read_camera_info(
    camera_info_id: int,
    db: Session = Depends(get_db)
):
    return CameraInfoService.get_camera_info(db, camera_info_id)


# 1.2. GET /api/v1/camera_infos/search：根据条件获取摄像头信息（支持分页）
@router.get("/search", response_model=Result[CameraInfoPageResponse], summary="根据条件获取摄像头信息（支持分页）")
def search_camera_infos(
        park_area: Optional[str] = Query(None, description="摄像头所处园区位置"),
        analysis_mode: Optional[int] = Query(None, description="分析模式: 0-无，1-全部，2-安全规范，3-区域入侵，4-火警"),
        camera_status: Optional[int] = Query(None, description="摄像头状态: 0-离线，1-在线"),
        skip: int = Query(0, description="跳过的记录数"),
        limit: int = Query(10, description="限制返回的记录数"),
        db: Session = Depends(get_db)
):
    """
    根据条件获取摄像头信息（支持分页）

    参数说明:
    - park_area: 摄像头所处园区位置
    - analysis_mode: 摄像头分析模式
    - camera_status: 摄像头状态
    - skip: 分页参数，跳过的记录数
    - limit: 分页参数，限制返回的记录数
    """
    return CameraInfoService.get_camera_infos_with_condition(
        db, park_area, analysis_mode, camera_status, skip, limit
    )

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

# 6.GET /api/v1/camera_infos/test/{camera_id} :测试摄像头能否连接
@router.get("/camera_infos/test/{camera_id}", response_model=Result, summary="测试摄像头能否连接")
def test_camera_connection(camera_id: str = "6", db: Session = Depends(get_db)):
    return CameraInfoService.test_camera_connection(camera_id, db)
