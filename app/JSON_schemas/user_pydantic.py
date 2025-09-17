from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ------------------- 响应模型（给前端返回数据的格式）-------------------
class UserResponse(BaseModel):
    user_id: int
    user_name: str
    name: str
    user_role: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True

# ------------------- 请求模型（前端传数据的格式校验）-------------------
class UserCreate(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=64, description="用户名")
    name: str = Field(..., min_length=1, max_length=64, description="用户姓名")
    password: str = Field(..., min_length=6, max_length=128, description="用户密码")
    user_role: Optional[int] = Field(None, ge=0, le=3, description="用户角色: 0-管理员 1-安保管理员 2-普通操作员")

class UserUpdate(BaseModel):
    user_name: Optional[str] = Field(None, min_length=1, max_length=64)
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    user_role: Optional[int] = Field(None, ge=0, le=3)