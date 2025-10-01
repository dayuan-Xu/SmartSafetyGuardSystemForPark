import asyncio
import threading
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
from app.crud.park_area_crud import get_park_area as crud_get_park_area
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
        
        # 获取园区区域名称
        park_area_info = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_get_park_area, db, db_camera_info.park_area_id
        )
        if park_area_info:
            # 创建包含园区区域名称的响应对象
            camera_response = CameraInfoResponse(
                camera_id=db_camera_info.camera_id,
                camera_name=db_camera_info.camera_name,
                park_area_id=db_camera_info.park_area_id,
                park_area=park_area_info.park_area,
                install_position=db_camera_info.install_position,
                rtsp_url=db_camera_info.rtsp_url,
                analysis_mode=db_camera_info.analysis_mode,
                camera_status=db_camera_info.camera_status,
                create_time=db_camera_info.create_time,
                update_time=db_camera_info.update_time
            )
            return Result.SUCCESS(camera_response)
        else:
            # 如果找不到园区区域信息，返回默认值
            camera_response = CameraInfoResponse(
                camera_id=db_camera_info.camera_id,
                camera_name=db_camera_info.camera_name,
                park_area_id=db_camera_info.park_area_id,
                park_area="未知区域",
                install_position=db_camera_info.install_position,
                rtsp_url=db_camera_info.rtsp_url,
                analysis_mode=db_camera_info.analysis_mode,
                camera_status=db_camera_info.camera_status,
                create_time=db_camera_info.create_time,
                update_time=db_camera_info.update_time
            )
            return Result.SUCCESS(camera_response)

    @staticmethod
    async def get_camera_infos_with_condition(
            db: Session,
            park_area_id: Optional[int] = None,
            analysis_mode: Optional[int] = None,
            camera_status: Optional[int] = None,
            skip: int = 0,
            limit: int = 10
    ) -> Result[CameraInfoPageResponse]:
        """
        根据条件获取摄像头信息（支持分页）

        Args:
            db: 数据库会话
            park_area_id: 园区位置ID
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
                db, park_area_id, analysis_mode, camera_status, skip, limit
            )
            
            # 获取每个摄像头对应的园区区域名称
            camera_responses = []
            for camera_info in camera_infos:
                park_area_info = await asyncio.get_event_loop().run_in_executor(
                    db_executor, crud_get_park_area, db, camera_info.park_area_id
                )
                park_area_name = park_area_info.park_area if park_area_info else "未知区域"
                
                camera_response = CameraInfoResponse(
                    camera_id=camera_info.camera_id,
                    camera_name=camera_info.camera_name,
                    park_area_id=camera_info.park_area_id,
                    park_area=park_area_name,
                    install_position=camera_info.install_position,
                    rtsp_url=camera_info.rtsp_url,
                    analysis_mode=camera_info.analysis_mode,
                    camera_status=camera_info.camera_status,
                    create_time=camera_info.create_time,
                    update_time=camera_info.update_time
                )
                camera_responses.append(camera_response)

            total = len(camera_responses)

            return Result.SUCCESS(CameraInfoPageResponse(total=total, rows=camera_responses))
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
        
        # 获取每个摄像头对应的园区区域名称
        camera_responses = []
        for camera_info in camera_infos:
            park_area_info = await asyncio.get_event_loop().run_in_executor(
                db_executor, crud_get_park_area, db, camera_info.park_area_id
            )
            park_area_name = park_area_info.park_area if park_area_info else "未知区域"
            
            camera_response = CameraInfoResponse(
                camera_id=camera_info.camera_id,
                camera_name=camera_info.camera_name,
                park_area_id=camera_info.park_area_id,
                park_area=park_area_name,
                install_position=camera_info.install_position,
                rtsp_url=camera_info.rtsp_url,
                analysis_mode=camera_info.analysis_mode,
                camera_status=camera_info.camera_status,
                create_time=camera_info.create_time,
                update_time=camera_info.update_time
            )
            camera_responses.append(camera_response)
        
        return Result.SUCCESS(camera_responses)

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
            # 检查园区区域是否存在
            park_area_info = await asyncio.get_event_loop().run_in_executor(
                db_executor, crud_get_park_area, db, camera_info.park_area_id
            )
            if not park_area_info:
                return Result.ERROR(f"园区区域ID {camera_info.park_area_id} 不存在")
            
            # 使用线程池执行数据库操作
            created_camera = await asyncio.get_event_loop().run_in_executor(
                db_executor, crud_create_camera_info, db, camera_info
            )
            
            # 创建包含园区区域名称的响应对象
            camera_response = CameraInfoResponse(
                camera_id=created_camera.camera_id,
                camera_name=created_camera.camera_name,
                park_area_id=created_camera.park_area_id,
                park_area=park_area_info.park_area,
                install_position=created_camera.install_position,
                rtsp_url=created_camera.rtsp_url,
                analysis_mode=created_camera.analysis_mode,
                camera_status=created_camera.camera_status,
                create_time=created_camera.create_time,
                update_time=created_camera.update_time
            )
            return Result.SUCCESS(camera_response)
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
        # 如果更新了园区区域ID，检查园区区域是否存在
        if camera_info_update.park_area_id is not None:
            park_area_info = await asyncio.get_event_loop().run_in_executor(
                db_executor, crud_get_park_area, db, camera_info_update.park_area_id
            )
            if not park_area_info:
                return Result.ERROR(f"园区区域ID {camera_info_update.park_area_id} 不存在")
        
        # 使用线程池执行数据库操作
        db_camera_info = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_update_camera_info, db, camera_info_id, camera_info_update
        )
        if not db_camera_info:
            return Result.ERROR(f"Update failure: CameraInfo not found with given id={camera_info_id}")
        
        # 获取园区区域名称
        park_area_info = await asyncio.get_event_loop().run_in_executor(
            db_executor, crud_get_park_area, db, db_camera_info.park_area_id
        )
        park_area_name = park_area_info.park_area if park_area_info else "未知区域"
        
        # 创建包含园区区域名称的响应对象
        camera_response = CameraInfoResponse(
            camera_id=db_camera_info.camera_id,
            camera_name=db_camera_info.camera_name,
            park_area_id=db_camera_info.park_area_id,
            park_area=park_area_name,
            install_position=db_camera_info.install_position,
            rtsp_url=db_camera_info.rtsp_url,
            analysis_mode=db_camera_info.analysis_mode,
            camera_status=db_camera_info.camera_status,
            create_time=db_camera_info.create_time,
            update_time=db_camera_info.update_time
        )
        return Result.SUCCESS(camera_response)

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
            result_container = {}

            def connection_task():
                try:
                    camera_info = get_camera_info(db, camera_id)
                    if not camera_info:
                        result_container['result'] = Result.ERROR(f"未找到ID为 {camera_id} 的摄像头信息")
                        return

                    cap = cv2.VideoCapture(camera_info.rtsp_url)
                    cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)
                    cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)

                    result_container['is_opened'] = cap.isOpened()
                    if cap.isOpened():
                        cap.release()
                        result_container['result'] = Result.SUCCESS(True, "RTSP流连接成功")
                    else:
                        result_container['result'] = Result.ERROR("RTSP流连接失败")

                except Exception as e:
                    result_container['result'] = Result.ERROR(f"测试连接时发生错误: {str(e)}")

            # 在单独线程中执行连接测试
            thread = threading.Thread(target=connection_task)
            thread.daemon = True
            thread.start()

            # 等待最多5秒
            thread.join(timeout=5.0)

            # 检查线程是否完成
            if thread.is_alive():
                return Result.ERROR("RTSP流连接超时（超过5秒）")

            return result_container['result']

        # 使用线程池执行阻塞的视频连接测试
        return await asyncio.get_event_loop().run_in_executor(db_executor, _test_connection)