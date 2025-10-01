from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.park_area_pydantic import ParkAreaResponse, ParkAreaCreate, ParkAreaUpdate, ParkAreaPageResponse
from app.dependencies.db import get_db  # 获取数据库会话的依赖
from app.services.park_area_service import ParkAreaService  # 导入service层代码负责业务逻辑

# 创建路由实例（tags 用于 API 文档分类）
router = APIRouter()

# 1. GET /api/v1/park_areas/search：根据条件获取园区区域信息（支持分页）
# 注意：这个路由必须放在 /{park_area_id} 之前，避免路由冲突
@router.get("/search", response_model=Result[ParkAreaPageResponse], summary="根据条件获取园区区域信息（支持分页）",
            status_code=status.HTTP_200_OK)
async def search_park_areas(
        park_area: Annotated[Optional[str], Query(description="园区区域名称")] = None,
        skip: Annotated[int, Query(description="跳过的记录数")] = 0,
        limit: Annotated[int, Query(description="限制返回的记录数")] = 10,
        db: Session = Depends(get_db)
):
    """
    根据条件获取园区区域信息（支持分页）

    Args:
        park_area (Optional[str]): 园区区域名称
        skip (int): 跳过的记录数
        limit (int): 限制返回的记录数
        db (Session): 数据库会话

    Returns:
        Result[ParkAreaPageResponse]: 包含园区区域信息分页结果的统一响应
    """
    result = await ParkAreaService.get_park_areas_with_condition(
        db, park_area, skip, limit
    )
    return result


# 2. GET /api/v1/park_areas/{park_area_id}：获取单个园区区域信息
@router.get("/{park_area_id}", response_model=Result[ParkAreaResponse], summary="获取单个园区区域信息",
            status_code=status.HTTP_200_OK)
async def read_park_area(
        park_area_id: Annotated[int, Path(title="园区区域ID", description="园区区域唯一标识")],
        db: Session = Depends(get_db)
):
    """
    根据ID获取单个园区区域信息

    Args:
        park_area_id (int): 园区区域唯一标识
        db (Session): 数据库会话

    Returns:
        Result[ParkAreaResponse]: 包含园区区域信息的统一响应结果
    """
    result = await ParkAreaService.get_park_area(db, park_area_id)
    return result


# 3. GET /api/v1/park_areas：获取所有园区区域信息（支持分页）
@router.get("/", response_model=Result[List[ParkAreaResponse]], summary="获取所有园区区域信息（支持分页）",
            status_code=status.HTTP_200_OK)
async def read_all_park_areas(
        skip: Annotated[int, Query(description="跳过的记录数")] = 0,
        limit: Annotated[int, Query(description="限制返回的记录数")] = 10,
        db: Session = Depends(get_db)
):
    """
    获取所有园区区域信息（支持分页）

    Args:
        skip (int): 跳过的记录数
        limit (int): 限制返回的记录数
        db (Session): 数据库会话

    Returns:
        Result[List[ParkAreaResponse]]: 包含园区区域信息列表的统一响应结果
    """
    result = await ParkAreaService.get_all_park_areas(db, skip=skip, limit=limit)
    return result


# 4. POST /api/v1/park_areas：创建新园区区域信息
@router.post("/", response_model=Result[ParkAreaResponse], summary="创建新园区区域信息",
            status_code=status.HTTP_201_CREATED)
async def create_new_park_area(
        park_area: ParkAreaCreate,
        db: Session = Depends(get_db)
):
    """
    创建新的园区区域信息

    Args:
        park_area (ParkAreaCreate): 园区区域信息创建数据
        db (Session): 数据库会话

    Returns:
        Result[ParkAreaResponse]: 包含创建的园区区域信息的统一响应结果
    """
    result = await ParkAreaService.create_park_area(db, park_area)
    return result


# 5. PUT /api/v1/park_areas/{park_area_id}：更新园区区域信息
@router.put("/{park_area_id}", response_model=Result[ParkAreaResponse], summary="更新园区区域信息",
            status_code=status.HTTP_200_OK)
async def update_park_area_info(
        park_area_id: Annotated[int, Path(title="园区区域ID", description="园区区域唯一标识")],
        park_area_update: ParkAreaUpdate,
        db: Session = Depends(get_db)
):
    """
    更新园区区域信息

    Args:
        park_area_id (int): 园区区域唯一标识
        park_area_update (ParkAreaUpdate): 园区区域信息更新数据
        db (Session): 数据库会话

    Returns:
        Result[ParkAreaResponse]: 包含更新后的园区区域信息的统一响应结果
    """
    result = await ParkAreaService.update_park_area(db, park_area_id, park_area_update)
    return result


# 6. DELETE /api/v1/park_areas/{park_area_ids}：删除园区区域信息（支持单个或批量删除）
@router.delete("/{park_area_ids}", response_model=Result, status_code=status.HTTP_200_OK,
            summary="删除园区区域信息（支持单个或批量删除）")
async def remove_park_area(
        park_area_ids: Annotated[str, Path(min_length=1, title="园区区域ID列表", description="园区区域ID列表，多个ID之间用英文逗号分隔")],
        db: Session = Depends(get_db)
):
    """
    删除园区区域信息（支持单个或批量删除）

    Args:
        park_area_ids (str): 园区区域ID列表，多个ID之间用英文逗号分隔
        db (Session): 数据库会话

    Returns:
        Result: 删除操作结果的统一响应
    """
    result = await ParkAreaService.delete_park_areas(db, park_area_ids)
    return result