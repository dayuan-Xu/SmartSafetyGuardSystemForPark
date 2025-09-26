from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ------------------- 响应模型（给前端返回数据的格式）-------------------
class UserResponse(BaseModel):
    user_id: int
    user_name: str
    name: str
    gender: int
    user_role: int
    phone: str
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True
        # API 文档示例数据
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "user_name": "zhangsan",
                "name": "张三",
                "gender": 1,
                "user_role": 2,
                "phone": "13800138000",
                "create_time": "2023-01-01T10:00:00",
                "update_time": "2023-01-01T10:00:00"
            }
        }

# ------------------- 请求模型（前端传数据的格式校验）-------------------

class UserRegister(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=64, description="用户名")
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str  = Field(..., min_length=6, max_length=128, description="用户密码")
    
    class Config:
        # API 文档示例数据
        json_schema_extra = {
            "example": {
                "user_name": "zhangsan",
                "phone": "13800138000",
                "password": "password123"
            }
        }

class UserCreate(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=64, description="用户名")
    name: str = Field(..., min_length=1, max_length=64, description="用户姓名")
    gender: Optional[int] = Field(1, ge=0, le=1, description="用户性别: 0-女 1-男")
    password: str = Field(..., min_length=6, max_length=128, description="用户密码")
    user_role: Optional[int] = Field(None, ge=0, le=3, description="用户角色: 0-管理员 1-安保管理员 2-普通操作员")
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")

class UserUpdate(BaseModel):
    user_name: Optional[str] = Field(None, min_length=1, max_length=64)
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    gender: Optional[int] = Field(None, ge=0, le=1)
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    user_role: Optional[int] = Field(None, ge=0, le=3)
    phone: Optional[str] = Field(None, min_length=11, max_length=11)

class UserPageResult(BaseModel):
    total: int
    rows: List[UserResponse]
    
    class Config:
        # API 文档示例数据
        json_schema_extra = {
            "example": {
                "total": 2,
                "rows": [
                    {
                        "user_id": 1,
                        "user_name": "zhangsan",
                        "name": "张三",
                        "gender": 1,
                        "user_role": 2,
                        "phone": "13800138000",
                        "create_time": "2023-01-01T10:00:00",
                        "update_time": "2023-01-01T10:00:00"
                    },
                    {
                        "user_id": 2,
                        "user_name": "lisi",
                        "name": "李四",
                        "gender": 0,
                        "user_role": 2,
                        "phone": "13800138001",
                        "create_time": "2023-01-02T10:00:00",
                        "update_time": "2023-01-02T10:00:00"
                    }
                ]
            }
        }