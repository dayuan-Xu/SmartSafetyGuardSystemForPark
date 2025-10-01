from datetime import datetime

import pytz
from sqlalchemy import Column, String, DateTime, Integer
from app.config.database import Base


class ParkAreaDB(Base):
    __tablename__ = "park_area"

    park_area_id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # 园区区域ID，主键自增，索引
    park_area = Column(String(64), unique=True, nullable=False)  # 园区区域名称，唯一，非空
    create_time = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Shanghai')))  # 创建时间
    update_time = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Shanghai')),onupdate=datetime.now(pytz.timezone('Asia/Shanghai')))  # 更新时间