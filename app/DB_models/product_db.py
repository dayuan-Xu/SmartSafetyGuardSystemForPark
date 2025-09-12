from sqlalchemy import Column, Integer, String, Float
from app.config.database import Base  # 继承配置中定义的 Base


# 商品表模型（对应 MySQL 中的 products 表）
class ProductDB(Base):
    __tablename__ = "product"  # 数据库表名

    # 字段定义
    id = Column(Integer, primary_key=True, index=True)  # 主键，自增
    name = Column(String(100), index=True, nullable=False)  # 商品名，非空
    price = Column(Float, nullable=False)  # 商品价格，非空
    stock = Column(Integer, default=0)  # 库存，默认 0