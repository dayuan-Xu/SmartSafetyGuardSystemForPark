from typing import List
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.camera_info_pydantic import CameraInfoResponse, CameraInfoCreate, CameraInfoUpdate
from app.crud.camera_crud import (
    get_camera_info as crud_get_camera_info,
    get_all_camera_infos as crud_get_all_camera_infos,
    create_camera_info as crud_create_camera_info,
    update_camera_info as crud_update_camera_info,
    delete_camera_infos as crud_delete_camera_infos
)
class CameraInfoService:
    @staticmethod
    def get_camera_info(db: Session, camera_info_id: int) -> Result[CameraInfoResponse]:
        """
        获取单个摄像头信息

        Args:
            db: 数据库会话
            camera_info_id: 摄像头信息ID

        Returns:
            Result[CameraInfoResponse]: 包含摄像头信息的响应对象
        """
        db_camera_info = crud_get_camera_info(db, camera_info_id)
        if not db_camera_info:
            return Result.ERROR(f"CameraInfo not found with given id={camera_info_id}")
        return Result.SUCCESS(db_camera_info)

    @staticmethod
    def get_all_camera_infos(db: Session, skip: int = 0, limit: int = 10) -> Result[List[CameraInfoResponse]]:
        """
        获取所有摄像头信息（支持分页）

        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 限制返回的记录数

        Returns:
            Result[List[CameraInfoResponse]]: 包含摄像头信息列表的响应对象
        """
        camera_infos = crud_get_all_camera_infos(db, skip=skip, limit=limit)
        return Result.SUCCESS(camera_infos)

    @staticmethod
    def create_camera_info(db: Session, camera_info: CameraInfoCreate) -> Result[CameraInfoResponse]:
        """
        创建新摄像头信息

        Args:
            db: 数据库会话
            camera_info: 摄像头信息创建请求数据

        Returns:
            Result[CameraInfoResponse]: 包含创建的摄像头信息的响应对象
        """
        try:
            created_camera = crud_create_camera_info(db, camera_info)
            return Result.SUCCESS(created_camera)
        except Exception as e:
            return Result.ERROR(f"创建摄像头信息失败: {str(e)}")

    @staticmethod
    def update_camera_info(db: Session, camera_info_id: int, camera_info_update: CameraInfoUpdate) -> Result[
        CameraInfoResponse]:
        """
        更新摄像头信息

        Args:
            db: 数据库会话
            camera_info_id: 摄像头信息ID
            camera_info_update: 摄像头信息更新请求数据

        Returns:
            Result[CameraInfoResponse]: 包含更新后的摄像头信息的响应对象
        """
        db_camera_info = crud_update_camera_info(db, camera_info_id, camera_info_update)
        if not db_camera_info:
            return Result.ERROR(f"Update failure: CameraInfo not found with given id={camera_info_id}")
        return Result.SUCCESS(db_camera_info)

    @staticmethod
    def delete_camera_infos(db: Session, camera_info_ids_str: str) -> Result:
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

        # 执行批量删除操作
        deleted_count = crud_delete_camera_infos(db, ids)

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
