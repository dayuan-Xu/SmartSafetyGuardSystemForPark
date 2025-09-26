import asyncio
from typing import List, Optional
import cv2
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.camera_info_pydantic import CameraInfoResponse, CameraInfoCreate, CameraInfoUpdate,CameraInfoPageResponse
from app.crud.camera_crud import (
    get_camera_info as crud_get_camera_info,
    get_camera_infos_with_condition as crud_get_camera_infos_with_condition,
    get_all_camera_infos as crud_get_all_camera_infos,
    create_camera_info as crud_create_camera_info,
    update_camera_info as crud_update_camera_info,
    delete_camera_infos as crud_delete_camera_infos, get_camera_info
)
from app.services.thread_pool_manager import executor as db_executor

class CameraInfoService:
    @staticmethod
    async def get_camera_info(db: Session, camera_info_id: int) -> Result[CameraInfoResponse]:
        """
        获取单个摄像头信息

        Args:
            db: 数据库会话
            camera_info_id: 摄像头信息ID

        Returns:
            Result[CameraInfoResponse]: 包含摄像头信息的响应对象
        """
        # 使用线程池执行数据库操作
        db_camera_info = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_get_camera_info, db, camera_info_id
        )
        if not db_camera_info:
            return Result.ERROR(f"CameraInfo not found with given id={camera_info_id}")
        return Result.SUCCESS(db_camera_info)

    @staticmethod
    async def get_camera_infos_with_condition(
            db: Session,
            park_area: Optional[str] = None,
            analysis_mode: Optional[int] = None,
            camera_status: Optional[int] = None,
            skip: int = 0,
            limit: int = 10
    ) -> Result[CameraInfoPageResponse]:
        """
        根据条件获取摄像头信息（支持分页）

        Args:
            db: 数据库会话
            park_area: 园区位置
            analysis_mode: 分析模式
            camera_status: 摄像头状态
            skip: 跳过的记录数
            limit: 限制返回的记录数

        Returns:
            Result[CameraInfoPageResponse]: 包含摄像头信息列表和分页信息的响应对象
        """
        try:
            # 使用线程池执行数据库操作
            camera_infos = await asyncio.get_event_loop().run_in_executor(
                db_executor,
                crud_get_camera_infos_with_condition,
                db, park_area, analysis_mode, camera_status, skip, limit
            )
            total = len(camera_infos)

            return Result.SUCCESS(CameraInfoPageResponse(total=total, rows=camera_infos))
        except Exception as e:
            return Result.ERROR(f"查询摄像头信息失败: {str(e)}")

    @staticmethod
    async def get_all_camera_infos(db: Session, skip: int = 0, limit: int = 10) -> Result[List[CameraInfoResponse]]:
        """
        获取所有摄像头信息（支持分页）

        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 限制返回的记录数

        Returns:
            Result[List[CameraInfoResponse]]: 包含摄像头信息列表的响应对象
        """
        # 使用线程池执行数据库操作
        camera_infos = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_get_all_camera_infos, db, skip, limit
        )
        return Result.SUCCESS(camera_infos)

    @staticmethod
    async def create_camera_info(db: Session, camera_info: CameraInfoCreate) -> Result[CameraInfoResponse]:
        """
        创建新摄像头信息

        Args:
            db: 数据库会话
            camera_info: 摄像头信息创建请求数据

        Returns:
            Result[CameraInfoResponse]: 包含创建的摄像头信息的响应对象
        """
        try:
            # 使用线程池执行数据库操作
            created_camera = await asyncio.get_event_loop().run_in_executor(
                db_executor, crud_create_camera_info, db, camera_info
            )
            return Result.SUCCESS(created_camera)
        except Exception as e:
            return Result.ERROR(f"创建摄像头信息失败: {str(e)}")

    @staticmethod
    async def update_camera_info(db: Session, camera_info_id: int, camera_info_update: CameraInfoUpdate) -> Result[CameraInfoResponse]:
        """
        更新摄像头信息

        Args:
            db: 数据库会话
            camera_info_id: 摄像头信息ID
            camera_info_update: 摄像头信息更新请求数据

        Returns:
            Result[CameraInfoResponse]: 包含更新后的摄像头信息的响应对象
        """
        # 使用线程池执行数据库操作
        db_camera_info = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_update_camera_info, db, camera_info_id, camera_info_update
        )
        if not db_camera_info:
            return Result.ERROR(f"Update failure: CameraInfo not found with given id={camera_info_id}")
        return Result.SUCCESS(db_camera_info)

    @staticmethod
    async def delete_camera_infos(db: Session, camera_info_ids_str: str) -> Result:
        """
        服务层处理摄像头信息删除业务逻辑并构造响应结果

        Args:
            db: 数据库会话
            camera_info_ids_str: 摄像头信息ID字符串（逗号分隔）

        Returns:
            Result: 包含删除结果的响应对象
        """
        # 解析ID列表，支持单个ID或多个ID（用逗号分隔）
        try:
            ids = [int(camera_id.strip()) for camera_id in camera_info_ids_str.split(',') if camera_id.strip()]
            if not ids:
                return Result.ERROR("无效的ID参数")
        except ValueError:
            return Result.ERROR("ID参数格式错误，请提供有效的数字ID")

        # 使用线程池执行数据库操作
        deleted_count = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_delete_camera_infos, db, ids
        )

        # 构造并返回响应结果
        if deleted_count == 0:
            return Result.ERROR("删除失败: 没有找到指定的任意一个摄像头信息")
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

    # rtsp流连通性检测方法
    @classmethod
    async def test_camera_connection(cls, camera_id, db):
        def _test_connection():
            try:
                camera_info = get_camera_info(db, camera_id)
                if not camera_info:
                    return Result.ERROR(f"未找到ID为 {camera_id} 的摄像头信息")

                cap = cv2.VideoCapture(camera_info.rtsp_url)
                cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)
                if cap.isOpened():
                    cap.release()
                    return Result.SUCCESS(True, "RTSP流连接成功")
                else:
                    return Result.ERROR("RTSP流连接失败")

            except Exception as e:
                return Result.ERROR(f"测试连接时发生错误: {str(e)}")

        # 使用线程池执行阻塞的视频连接测试
        return await asyncio.get_event_loop().run_in_executor(db_executor, _test_connection,)