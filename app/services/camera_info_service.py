from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.crud.camera_crud import delete_camera_infos as crud_delete_camera_infos


class CameraInfoService:
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
