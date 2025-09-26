from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.camera_info_pydantic import CameraInfoResponse, CameraInfoCreate, CameraInfoUpdate,CameraInfoPageResponse
from app.dependencies.db import get_db  # 获取数据库会话的依赖
from app.services.camera_info_service import CameraInfoService  # 导入service层代码负责业务逻辑
from app.dependencies.security import get_current_active_user, User

# 创建路由实例（tags 用于 API 文档分类）
router = APIRouter()

# 1. GET /api/v1/camera_infos/search：根据条件获取摄像头信息（支持分页）
# 注意：这个路由必须放在 /{camera_info_id} 之前，避免路由冲突
@router.get("/search", response_model=Result[CameraInfoPageResponse], summary="根据条件获取摄像头信息（支持分页）", status_code=status.HTTP_200_OK)
async def search_camera_infos(
        park_area: Annotated[Optional[str], Query(description="摄像头所处园区位置")] = None,
        analysis_mode: Annotated[Optional[int], Query(description="分析模式: 0-无，1-全部，2-安全规范，3-区域入侵，4-火警")] = None,
        camera_status: Annotated[Optional[int], Query(description="摄像头状态: 0-离线，1-在线")] = None,
        skip: Annotated[int, Query(description="跳过的记录数")] = 0,
        limit: Annotated[int, Query(description="限制返回的记录数")] = 10,
        db: Session = Depends(get_db)
):
    """
    根据条件获取摄像头信息（支持分页）

    Args:
        park_area (Optional[str]): 摄像头所处园区位置
        analysis_mode (Optional[int]): 摄像头分析模式
        camera_status (Optional[int]): 摄像头状态
        skip (int): 跳过的记录数
        limit (int): 限制返回的记录数
        db (Session): 数据库会话

    Returns:
        Result[CameraInfoPageResponse]: 包含摄像头信息分页结果的统一响应
    """
    result = await CameraInfoService.get_camera_infos_with_condition(
        db, park_area, analysis_mode, camera_status, skip, limit
    )
    return result

# 2. GET /api/v1/camera_infos/{camera_info_id}：获取单个摄像头信息
@router.get("/{camera_info_id}", response_model=Result[CameraInfoResponse], summary="获取单个摄像头信息", status_code=status.HTTP_200_OK)
async def read_camera_info(
    camera_info_id: Annotated[int, Path(title="摄像头信息ID", description="摄像头信息唯一标识")],
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个摄像头信息

    Args:
        camera_info_id (int): 摄像头信息唯一标识
        db (Session): 数据库会话

    Returns:
        Result[CameraInfoResponse]: 包含摄像头信息的统一响应结果
    """
    result = await CameraInfoService.get_camera_info(db, camera_info_id)
    return result

# 3. GET /api/v1/camera_infos：获取所有摄像头信息（支持分页）
@router.get("/", response_model=Result[List[CameraInfoResponse]], summary="获取所有摄像头信息（支持分页）", status_code=status.HTTP_200_OK)
async def read_all_camera_infos(
    skip: Annotated[int, Query(description="跳过的记录数")] = 0,
    limit: Annotated[int, Query(description="限制返回的记录数")] = 10,
    db: Session = Depends(get_db)
):
    """
    获取所有摄像头信息（支持分页）

    Args:
        skip (int): 跳过的记录数
        limit (int): 限制返回的记录数
        db (Session): 数据库会话

    Returns:
        Result[List[CameraInfoResponse]]: 包含摄像头信息列表的统一响应结果
    """
    result = await CameraInfoService.get_all_camera_infos(db, skip=skip, limit=limit)
    return result

# 4. POST /api/v1/camera_infos：创建新摄像头信息
@router.post("/", response_model=Result[CameraInfoResponse], status_code=status.HTTP_201_CREATED, summary="创建新摄像头信息")
async def create_new_camera_info(
    camera_info: CameraInfoCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的摄像头信息

    Args:
        camera_info (CameraInfoCreate): 摄像头信息创建数据
        db (Session): 数据库会话

    Returns:
        Result[CameraInfoResponse]: 包含新创建的摄像头信息的统一响应结果
    """
    result = await CameraInfoService.create_camera_info(db, camera_info)
    return result

# 5. PUT /api/v1/camera_infos/{camera_info_id}：修改摄像头信息
@router.put("/{camera_info_id}", response_model=Result[CameraInfoResponse], summary="修改摄像头信息", status_code=status.HTTP_200_OK)
async def update_existing_camera_info(
    camera_info_id: Annotated[int, Path(title="摄像头信息ID", description="摄像头信息唯一标识")],
    camera_info_update: CameraInfoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),

):
    """
    修改摄像头信息

    Args:
        camera_info_id (int): 摄像头信息唯一标识
        camera_info_update (CameraInfoUpdate): 摄像头信息更新数据
        db (Session): 数据库会话
        current_user (User): 当前登录用户信息

    Returns:
        Result[CameraInfoResponse]: 包含更新后的摄像头信息的统一响应结果
    """
    print("current_user:", current_user)
    result = await CameraInfoService.update_camera_info(db, camera_info_id, camera_info_update)
    return result

# 6. DELETE /api/v1/camera_infos/{camera_info_ids}：删除摄像头信息（支持单个或批量删除）
@router.delete("/{camera_info_ids}", response_model=Result, status_code=status.HTTP_200_OK, summary="删除摄像头信息（支持单个或批量删除）")
async def remove_camera_info(
    camera_info_ids: Annotated[str, Path(min_length=1, title="摄像头信息ID列表", description="摄像头信息ID列表，多个ID之间用英文逗号分隔")],
    db: Session = Depends(get_db)
):
    """
    删除摄像头信息（支持单个或批量删除）

    Args:
        camera_info_ids (str): 摄像头信息ID列表，多个ID之间用英文逗号分隔
        db (Session): 数据库会话

    Returns:
        Result: 删除操作结果的统一响应
    """
    result = await CameraInfoService.delete_camera_infos(db, camera_info_ids)
    return result

# 7. GET /api/v1/camera_infos/test/{camera_id} :测试摄像头能否连接
@router.get("/test/{camera_id}", response_model=Result, summary="测试摄像头能否连接", status_code=status.HTTP_200_OK)
async def test_camera_connection(
    camera_id: Annotated[str, Path(title="摄像头ID", description="摄像头唯一标识")], 
    db: Session = Depends(get_db)
):  # 注意这里camera_id是字符串
    """
    测试摄像头能否连接

    Args:
        camera_id (str): 摄像头唯一标识
        db (Session): 数据库会话

    Returns:
        Result: 测试结果的统一响应
    """
    result = await CameraInfoService.test_camera_connection(camera_id, db)
    return result