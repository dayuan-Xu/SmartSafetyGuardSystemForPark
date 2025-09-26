from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

# 定义泛型类型变量，支持任意数据类型
T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    """统一API响应模型"""
    code: int = Field(1, description="业务状态码：0=失败，非0=成功")
    msg: str = Field("操作成功", description="提示信息")
    data: Optional[T] = Field(None, description="业务数据，失败时为null")

    @staticmethod
    def SUCCESS(data: T, msg: str = "操作成功") -> "Result[T]":
        """成功响应：默认code=1，需传入data，可选自定义msg"""
        return Result(
            code=1,
            msg=msg,
            data=data
        )

    @staticmethod
    def ERROR(msg: str, data: Optional[T] = None) -> "Result[T]":
        """失败响应：默认code=0（通用错误），需传入msg，可选自定义data（通常为null）"""
        return Result(
            code=0,  # 可根据需求改为更具体的错误码，如1000
            msg=msg,
            data=data
        )

    class Config:
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
        
        pass  # 移除示例数据以避免覆盖泛型参数的具体示例数据