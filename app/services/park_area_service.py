import asyncio
from typing import List, Optional

from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.park_area_pydantic import ParkAreaResponse, ParkAreaCreate, ParkAreaUpdate, ParkAreaPageResponse
from app.crud.park_area_crud import (
    get_park_area as crud_get_park_area,
    get_park_areas_with_condition as crud_get_park_areas_with_condition,
    get_all_park_areas as crud_get_all_park_areas,
    create_park_area as crud_create_park_area,
    update_park_area as crud_update_park_area,
    delete_park_areas as crud_delete_park_areas,
    get_park_area_by_name as crud_get_park_area_by_name
)
from app.services.thread_pool_manager import executor as db_executor


class ParkAreaService:
    @staticmethod
    async def get_park_area(db: Session, park_area_id: int) -> Result[ParkAreaResponse]:
        """
        获取单个园区区域信息

        Args:
            db: 数据库会话
            park_area_id: 园区区域ID

        Returns:
            Result[ParkAreaResponse]: 包含园区区域信息的响应对象
        """
        # 使用线程池执行数据库操作
        db_park_area = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_get_park_area, db, park_area_id
        )
        if not db_park_area:
            return Result.ERROR(f"ParkArea not found with given id={park_area_id}")
        return Result.SUCCESS(db_park_area)

    @staticmethod
    async def get_park_area_by_name(db: Session, park_area: str) -> Result[ParkAreaResponse]:
        """
        根据名称获取园区区域信息

        Args:
            db: 数据库会话
            park_area: 园区区域名称

        Returns:
            Result[ParkAreaResponse]: 包含园区区域信息的响应对象
        """
        # 使用线程池执行数据库操作
        db_park_area = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_get_park_area_by_name, db, park_area
        )
        if not db_park_area:
            return Result.ERROR(f"ParkArea not found with given name={park_area}")
        return Result.SUCCESS(db_park_area)

    @staticmethod
    async def get_park_areas_with_condition(
            db: Session,
            park_area: Optional[str] = None,
            skip: int = 0,
            limit: int = 10
    ) -> Result[ParkAreaPageResponse]:
        """
        根据条件获取园区区域信息（支持分页）

        Args:
            db: 数据库会话
            park_area: 园区区域名称
            skip: 跳过的记录数
            limit: 限制返回的记录数

        Returns:
            Result[ParkAreaPageResponse]: 包含园区区域信息列表和分页信息的响应对象
        """
        try:
            # 使用线程池执行数据库操作
            park_areas = await asyncio.get_event_loop().run_in_executor(
                db_executor,
                crud_get_park_areas_with_condition,
                db, park_area, skip, limit
            )
            total = len(park_areas)

            return Result.SUCCESS(ParkAreaPageResponse(total=total, rows=park_areas))
        except Exception as e:
            return Result.ERROR(f"查询园区区域信息失败: {str(e)}")

    @staticmethod
    async def get_all_park_areas(db: Session, skip: int = 0, limit: int = 10) -> Result[List[ParkAreaResponse]]:
        """
        获取所有园区区域信息（支持分页）

        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 限制返回的记录数

        Returns:
            Result[List[ParkAreaResponse]]: 包含园区区域信息列表的响应对象
        """
        # 使用线程池执行数据库操作
        park_areas = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_get_all_park_areas, db, skip, limit
        )
        return Result.SUCCESS(park_areas)

    @staticmethod
    async def create_park_area(db: Session, park_area: ParkAreaCreate) -> Result[ParkAreaResponse]:
        """
        创建新园区区域信息

        Args:
            db: 数据库会话
            park_area: 园区区域信息创建请求数据

        Returns:
            Result[ParkAreaResponse]: 包含创建的园区区域信息的响应对象
        """
        try:
            # 检查是否已存在同名园区区域
            existing_park_area = await asyncio.get_event_loop().run_in_executor(
                db_executor, crud_get_park_area_by_name, db, park_area.park_area
            )
            if existing_park_area:
                return Result.ERROR(f"园区区域 '{park_area.park_area}' 已存在")

            # 使用线程池执行数据库操作
            created_park_area = await asyncio.get_event_loop().run_in_executor(
                db_executor, crud_create_park_area, db, park_area
            )
            return Result.SUCCESS(created_park_area)
        except Exception as e:
            return Result.ERROR(f"创建园区区域信息失败: {str(e)}")

    @staticmethod
    async def update_park_area(db: Session, park_area_id: int, park_area_update: ParkAreaUpdate) -> Result[
        ParkAreaResponse]:
        """
        更新园区区域信息

        Args:
            db: 数据库会话
            park_area_id: 园区区域ID
            park_area_update: 园区区域信息更新请求数据

        Returns:
            Result[ParkAreaResponse]: 包含更新后的园区区域信息的响应对象
        """
        # 检查是否尝试更新为已存在的名称
        if park_area_update.park_area:
            existing_park_area = await asyncio.get_event_loop().run_in_executor(
                db_executor, crud_get_park_area_by_name, db, park_area_update.park_area
            )
            if existing_park_area and existing_park_area.park_area_id != park_area_id:
                return Result.ERROR(f"园区区域 '{park_area_update.park_area}' 已存在")

        # 使用线程池执行数据库操作
        db_park_area = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_update_park_area, db, park_area_id, park_area_update
        )
        if not db_park_area:
            return Result.ERROR(f"Update failure: ParkArea not found with given id={park_area_id}")
        return Result.SUCCESS(db_park_area)

    @staticmethod
    async def delete_park_areas(db: Session, park_area_ids_str: str) -> Result:
        """
        服务层处理园区区域信息删除业务逻辑并构造响应结果

        Args:
            db: 数据库会话
            park_area_ids_str: 园区区域ID字符串（逗号分隔）

        Returns:
            Result: 包含删除结果的响应对象
        """
        # 解析ID列表，支持单个ID或多个ID（用逗号分隔）
        try:
            ids = [int(park_area_id.strip()) for park_area_id in park_area_ids_str.split(',') if park_area_id.strip()]
            if not ids:
                return Result.ERROR("无效的ID参数")
        except ValueError:
            return Result.ERROR("ID参数格式错误，请提供有效的数字ID")

        # 使用线程池执行数据库操作
        deleted_count = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_delete_park_areas, db, ids
        )

        # 构造并返回响应结果
        if deleted_count == 0:
            return Result.ERROR("删除失败: 没有找到指定的任意一个园区区域信息")
        elif deleted_count < len(ids):
            return Result.SUCCESS(
                {"deleted_count": deleted_count},
                f"部分删除成功: 成功删除{deleted_count}条记录"
            )
        else:
            return Result.SUCCESS(
                {"deleted_count": deleted_count},
                f"批量删除成功: 共删除{deleted_count}条记录"
            )