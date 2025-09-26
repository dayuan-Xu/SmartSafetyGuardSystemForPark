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
        # API 文档示例数据
        json_schema_extra = {
            "example": {
                "camera_id": 1,
                "camera_name": "东门摄像头",
                "park_area": "东区",
                "install_position": "东门岗亭上方",
                "rtsp_url": "rtsp://192.168.1.1:554/live.sdp",
                "analysis_mode": 1,
                "camera_status": 1,
                "create_time": "2023-01-01T10:00:00",
                "update_time": "2023-01-01T10:00:00"
            }
        }

class CameraInfoPageResponse(BaseModel):
    total: int
    rows: List[CameraInfoResponse]
    
    class Config:
        # API 文档示例数据
        json_schema_extra = {
            "example": {
                "total": 2,
                "rows": [
                    {
                        "camera_id": 1,
                        "camera_name": "东门摄像头",
                        "park_area": "东区",
                        "install_position": "东门岗亭上方",
                        "rtsp_url": "rtsp://192.168.1.1:554/live.sdp",
                        "analysis_mode": 1,
                        "camera_status": 1,
                        "create_time": "2023-01-01T10:00:00",
                        "update_time": "2023-01-01T10:00:00"
                    },
                    {
                        "camera_id": 2,
                        "camera_name": "西门摄像头",
                        "park_area": "西区",
                        "install_position": "西门岗亭上方",
                        "rtsp_url": "rtsp://192.168.1.2:554/live.sdp",
                        "analysis_mode": 2,
                        "camera_status": 1,
                        "create_time": "2023-01-01T11:00:00",
                        "update_time": "2023-01-01T11:00:00"
                    }
                ]
            }
        }

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