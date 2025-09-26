from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ------------------- 响应模型（给前端返回数据的格式）-------------------
class AlarmHandleRecordResponse(BaseModel):
    handle_id: int
    alarm_id: int
    handle_time: datetime
    handler_user_id: int
    handle_action: int
    handle_content: Optional[str] = None
    handle_attachment_url: Optional[str] = None
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True
        # API 文档示例数据
        json_schema_extra = {
            "example": {
                "handle_id": 1,
                "alarm_id": 101,
                "handle_time": "2023-01-01T10:00:00",
                "handler_user_id": 1,
                "handle_action": 2,
                "handle_content": "已派遣人员处理",
                "handle_attachment_url": "https://oss.example.com/attachment.jpg",
                "create_time": "2023-01-01T10:00:00",
                "update_time": "2023-01-01T10:00:00"
            }
        }

# ------------------- 请求模型（接收前端请求数据的格式）-------------------
class AlarmHandleRecordCreate(BaseModel):
    alarm_id: int
    handle_action: int
    handle_content: Optional[str] = Field(None, max_length=255, description="处理详情（如派单对象、解决措施），可为空，处理动作为派单时前端根据所选普通操作员自动生成处理详情,比如'已经派遣普通操作员 王芳 前往处理'")
    handle_attachment_url: Optional[str] = Field(None, max_length=255, description="处理附件上传到OSS后返回的URL，可为空")
    handler_user_id: int= Field(..., ge=1, le=2147483647, description="处理人ID")


class AlarmAttachmentUpload(BaseModel):
    file_content: str = Field(..., description="Base64编码的文件内容")
    file_extension: str = Field(..., description="文件扩展名，例如 '.jpg', '.png'", pattern=r"^\.[a-zA-Z0-9]+$")

    @field_validator('file_extension')
    @classmethod
    def validate_file_extension(cls, v):
        """
        验证文件扩展名是否为支持的类型
        """
        supported_extensions = {
            # 图片格式
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
            # 视频格式
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'
        }
        if v.lower() not in supported_extensions:
            raise ValueError(f'不支持的文件类型: {v}。支持的类型包括: {", ".join(supported_extensions)}')
        return v