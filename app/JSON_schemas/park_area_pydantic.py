from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

# ------------------- 响应模型（给前端返回数据的格式）-------------------
class ParkAreaResponse(BaseModel):
    park_area_id: int
    park_area: str
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True
        # API 文档示例数据
        json_schema_extra = {
            "example": {
                "park_area_id": 1,
                "park_area": "东区",
                "create_time": "2023-01-01T10:00:00",
                "update_time": "2023-01-01T10:00:00"
            }
        }

class ParkAreaPageResponse(BaseModel):
    total: int
    rows: List[ParkAreaResponse]
    
    class Config:
        # API 文档示例数据
        json_schema_extra = {
            "example": {
                "total": 2,
                "rows": [
                    {
                        "park_area_id": 1,
                        "park_area": "东区",
                        "create_time": "2023-01-01T10:00:00",
                        "update_time": "2023-01-01T10:00:00"
                    },
                    {
                        "park_area_id": 2,
                        "park_area": "西区",
                        "create_time": "2023-01-01T11:00:00",
                        "update_time": "2023-01-01T11:00:00"
                    }
                ]
            }
        }

# ------------------- 请求模型（前端传数据的格式校验）-------------------
class ParkAreaCreate(BaseModel):
    park_area: str = Field(..., min_length=1, max_length=64, description="园区区域名称")

class ParkAreaUpdate(BaseModel):
    park_area: Optional[str] = Field(None, min_length=1, max_length=64, description="园区区域名称")