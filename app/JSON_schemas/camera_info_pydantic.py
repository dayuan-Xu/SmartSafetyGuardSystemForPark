from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ------------------- 响应模型（给前端返回数据的格式）-------------------
class CameraInfoResponse(BaseModel):
    camera_id: int
    camera_name: str
    park_area: str
    install_position: str
    rtsp_url: str
    analysis_mode: int
    camera_status: int
    create_time: datetime
    update_time: datetime

    # 允许 Pydantic 模型从 SQLAlchemy 模型（CameraInfoDB）实例中读取数据
    class Config:
        from_attributes = True

class CameraInfoPageResponse(BaseModel):
    total: int
    rows: List[CameraInfoResponse]

# ------------------- 请求模型（前端传数据的格式校验）-------------------
class CameraInfoCreate(BaseModel):
    camera_name: str = Field(..., min_length=1, max_length=64, description="摄像头名称")
    park_area: str = Field(..., min_length=1, max_length=64, description="摄像头所属园区区域")
    install_position: str = Field(..., min_length=1, max_length=64, description="摄像头具体安装位置")
    rtsp_url: str = Field(..., min_length=1, max_length=255, description="摄像头的RTSP地址")
    analysis_mode: int = Field(..., ge=0, le=4, description="分析模式: 0-无，1-全部，2-安全规范，3-区域入侵，4-火警")

# 修改摄像头信息时的请求模型（允许部分字段修改，所以用 Optional）
class CameraInfoUpdate(BaseModel):
    camera_name: Optional[str] = Field(None, min_length=1, max_length=64)
    park_area: Optional[str] = Field(None, min_length=1, max_length=64)
    install_position: Optional[str] = Field(None, min_length=1, max_length=64)
    rtsp_url: Optional[str] = Field(None, min_length=1, max_length=255)
    analysis_mode: Optional[int] = Field(None, ge=0, le=4)
