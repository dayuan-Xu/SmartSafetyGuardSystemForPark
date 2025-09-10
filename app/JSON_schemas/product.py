from pydantic import BaseModel, Field
from typing import Optional, List

# ------------------- 响应模型（给前端返回数据的格式）-------------------
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: Optional[int] = 0  # 可选字段，默认 0

    # 允许 Pydantic 模型从 SQLAlchemy 模型（ProductDB）实例中读取数据
    class Config:
        orm_mode = True

# ------------------- 请求模型（前端传数据的格式校验）-------------------
class ProductCreate(BaseModel):
    # Field 用于更精细的校验：商品名至少 2 个字符，价格大于 0
    name: str = Field(..., min_length=2, description="商品名称，至少 2 个字符")
    price: float = Field(..., gt=0, description="商品价格，必须大于 0")
    stock: Optional[int] = Field(0, ge=0, description="库存，非负整数")

# 修改商品时的请求模型（允许部分字段修改，所以用 Optional）
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)