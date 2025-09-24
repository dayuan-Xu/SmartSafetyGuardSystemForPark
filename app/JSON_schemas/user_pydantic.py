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

# ------------------- 请求模型（前端传数据的格式校验）-------------------
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