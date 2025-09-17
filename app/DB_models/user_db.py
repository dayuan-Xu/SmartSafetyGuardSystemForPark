from datetime import datetime

import pytz
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.mssql import TINYINT

from app.config.database import Base


class UserDB(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True,autoincrement=True, index=True) # 用户ID, 主键, 索引,自增
    user_name = Column(String(64), unique=True,nullable=False) # 用户名，非空，唯一
    name = Column(String(64),nullable=False) # 姓名，非空
    password = Column(String(128), nullable=False)  # 存储加密后的密码, 非空
    user_role = Column(TINYINT, default=3)  # 0-管理员 1-安保管理员 2-普通操作员
    create_time = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Shanghai'))) # 创建时间
    update_time = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Shanghai')), onupdate=datetime.now(pytz.timezone('Asia/Shanghai')))# 更新时间