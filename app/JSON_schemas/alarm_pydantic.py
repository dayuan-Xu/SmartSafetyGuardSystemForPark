from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class AlarmResponse(BaseModel):
    alarm_id: int
    camera_id: int
    alarm_type: int
    alarm_status: int
    alarm_time: datetime
    alarm_end_time: Optional[datetime] = None
    snapshot_url: str
    create_time: datetime
    update_time: datetime
    park_area: str
    camera_name: str
    handle_user_name: Optional[str] = None

    class Config:
        from_attributes = True
        # API 文档示例数据
        json_schema_extra = {
            "example": {
                "alarm_id": 1,
                "camera_id": 1,
                "alarm_type": 2,
                "alarm_status": 1,
                "alarm_time": "2023-01-01T10:00:00",
                "alarm_end_time": "2023-01-01T10:05:00",
                "snapshot_url": "https://oss.example.com/snapshot.jpg",
                "create_time": "2023-01-01T10:00:00",
                "update_time": "2023-01-01T10:05:00",
                "park_area": "东区",
                "camera_name": "东门摄像头",
                "handle_user_name": "张三"
            }
        }

class AlarmPageResponse(BaseModel):
    total: int
    rows: List[AlarmResponse]
    
    class Config:
        # API 文档示例数据
        json_schema_extra = {
            "example": {
                "total": 2,
                "rows": [
                    {
                        "alarm_id": 1,
                        "camera_id": 1,
                        "alarm_type": 2,
                        "alarm_status": 1,
                        "alarm_time": "2023-01-01T10:00:00",
                        "alarm_end_time": "2023-01-01T10:05:00",
                        "snapshot_url": "https://oss.example.com/snapshot1.jpg",
                        "create_time": "2023-01-01T10:00:00",
                        "update_time": "2023-01-01T10:05:00",
                        "park_area": "东区",
                        "camera_name": "东门摄像头",
                        "handle_user_name": "张三"
                    },
                    {
                        "alarm_id": 2,
                        "camera_id": 2,
                        "alarm_type": 1,
                        "alarm_status": 0,
                        "alarm_time": "2023-01-01T11:00:00",
                        "alarm_end_time": None,
                        "snapshot_url": "https://oss.example.com/snapshot2.jpg",
                        "create_time": "2023-01-01T11:00:00",
                        "update_time": "2023-01-01T11:00:00",
                        "park_area": "西区",
                        "camera_name": "西门摄像头",
                        "handle_user_name": None
                    }
                ]
            }
        }

class AlarmQueryParams(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    alarm_type: Optional[int] = None
    alarm_status: Optional[int] = None
    skip: int = 0
    limit: int = 10