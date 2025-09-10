from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Text
from datetime import datetime
from app.config.database import Base


class AlarmMain(Base):
    __tablename__ = "alarm_main"

    alarm_id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    camera_id = Column(String(32), nullable=False, index=True)
    alarm_type = Column(Integer, nullable=False)  # 1-未戴安全帽
    alarm_level = Column(Integer, default=2)  # 2-中风险
    alarm_status = Column(Integer, default=0)  # 0-未处理
    alarm_time = Column(DateTime, default=datetime.utcnow)
    alarm_desc = Column(Text, nullable=True)
    snapshot_url = Column(String(255), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)