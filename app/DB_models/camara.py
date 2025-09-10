from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
from app.config.database import Base


class CameraInfo(Base):
    __tablename__ = "camera_info"

    camera_id = Column(String(32), primary_key=True, index=True)
    camera_name = Column(String(64), nullable=False)
    park_area = Column(String(64), nullable=False)
    rtsp_url = Column(String(255), nullable=False)
    camera_status = Column(Integer, default=0)  # 0-离线，1-在线
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)