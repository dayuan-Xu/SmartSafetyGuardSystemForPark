from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

# 定义泛型类型变量，支持任意数据类型
T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    """统一API响应模型"""
    code: int = Field(..., description="业务状态码：0=失败，非0=成功")
    msg: str = Field(..., description="提示信息")
    data: Optional[T] = Field(None, description="业务数据，失败时为null")

    @staticmethod
    def SUCCESS(data: T, msg: str = "操作成功") -> "Result[T]":
        """成功响应：默认code=0，需传入data，可选自定义msg"""
        return Result(
            code=1,
            msg=msg,
            data=data
        )

    @staticmethod
    def ERROR(msg: str, data: Optional[T] = None) -> "Result[T]":
        """失败响应：默认code=1（通用错误），需传入msg，可选自定义data（通常为null）"""
        return Result(
            code=0,  # 可根据需求改为更具体的错误码，如1000
            msg=msg,
            data=data
        )

    class Config:
        # API 文档示例数据 - 成功和失败两种情况
        json_schema_extra = {
            "examples": [
                {
                    "code": 1,
                    "msg": "操作成功",
                    "data": {"camera_id": 1,
                             "camera_name": "东门摄像头",
                             "park_area": "东区",
                             "install_position":"东门岗亭上方",
                             "rtsp_url": "rtsp://192.168.1.1:554/live.sdp"
                             }
                },

                {
                    "code": 1,
                    "msg": "操作成功",
                    "data": [
                        {"camera_id": 1, "camera_name": "东门摄像头"},
                        {"camera_id": 2, "camera_name": "西门摄像头"}
                    ]
                },
                {
                    "code": 1,
                    "msg": "删除成功",
                    "data": None
                },
                {
                    "code": 0,
                    "msg": "操作失败: CameraInfo with id 1 not found",
                    "data": None
                }
            ]
        }

        # 允许从 ORM 对象中读取数据（适用于 SQLAlchemy 等 ORM）
        from_attributes = True

        # 忽略模型中未定义的额外字段
        extra = "ignore"

        # 自定义 JSON 编码器
        json_encoders = {
            # 可以添加自定义类型的序列化方式
            # datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S"),
            # Decimal: lambda v: float(v)
        }


