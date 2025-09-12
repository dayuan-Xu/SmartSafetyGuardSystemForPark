from datetime import datetime
import pytz
from sqlalchemy import Column, String, DateTime, Integer
from app.config.database import Base


class CameraInfoDB(Base):
    __tablename__ = "camera_info"

    camera_id = Column(Integer, primary_key=True, autoincrement=True, index=True) # 摄像头ID，主键自增，索引
    camera_name = Column(String(64), nullable=False) # 摄像头名称，非空
    park_area = Column(String(64), nullable=False) #  摄像头所属园区区域，非空
    install_position = Column(String(64), nullable=False) #  摄像头具体安装位置，非空
    rtsp_url = Column(String(255), nullable=False) # 摄像头的RTSP地址，非空
    analysis_mode=Column(Integer, nullable=False)# 分析模式: 0-无，1-全部，2-安全规范， 3-区域入侵， 4-火警
    camera_status = Column(Integer, default=0)  # 摄像头状态：0-离线，1-在线
    create_time = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Shanghai'))) # 创建时间
    update_time = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Shanghai')), onupdate=datetime.now(pytz.timezone('Asia/Shanghai'))) # 更新时间