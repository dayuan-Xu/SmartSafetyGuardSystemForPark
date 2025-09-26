from datetime import datetime

import pytz
from sqlalchemy import Column, BigInteger, String, DateTime, Integer
from sqlalchemy.dialects.mssql import TINYINT

from app.config.database import Base


class AlarmDB(Base):
    __tablename__ = "alarm"

    alarm_id = Column(BigInteger, primary_key=True, autoincrement=True, index=True) # 报警ID，唯一自增，建索引
    camera_id = Column(Integer, nullable=False, index=True)# 摄像头ID，逻辑外键，建索引
    alarm_type = Column(TINYINT(), nullable=False)  # 0-安全规范（未戴安全帽/未穿反光衣） 2-区域入侵（人/车） 3-火警（火焰/烟雾）
    alarm_status = Column(TINYINT(), default=0)  # 0-未处理 1-确认误报 2-处理中（已派单） 3-处理完成
    alarm_time = Column(DateTime, nullable=False) # 告警触发时间，非空
    alarm_end_time = Column(DateTime, nullable=True) # 告警触发时间，可为空
    snapshot_url = Column(String(255), nullable=False) # 报警截图URL，非空 （对于安全规范告警，该字段最多包含2张截图的URL）
    create_time = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Shanghai')))  # 创建时间
    update_time = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Shanghai')), onupdate=datetime.now(pytz.timezone('Asia/Shanghai'))) # 更新时间