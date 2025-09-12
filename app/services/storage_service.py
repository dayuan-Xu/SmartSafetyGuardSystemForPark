import os
import cv2
from datetime import datetime
from sqlalchemy.orm import Session
from app.DB_models.alarm_db import AlarmMain
from dotenv import load_dotenv

load_dotenv()
SNAPSHOT_PATH = os.getenv('SNAPSHOT_PATH')

# 确保截图目录存在
os.makedirs(SNAPSHOT_PATH, exist_ok=True)


class StorageService:
    @staticmethod
    def save_snapshot(frame, camera_id):
        """保存截图并返回存储路径"""
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{camera_id}_{timestamp}.jpg"
        filepath = os.path.join(SNAPSHOT_PATH, filename)

        # 保存图像
        cv2.imwrite(filepath, frame)
        return filepath

    @staticmethod
    def save_alarm_record(db: Session, camera_id, snapshot_url, desc="未戴安全帽检测"):
        """保存告警记录到数据库"""
        alarm = AlarmMain(
            camera_id=camera_id,
            alarm_type=1,  # 1-未戴安全帽
            snapshot_url=snapshot_url,
            alarm_desc=desc
        )
        db.add(alarm)
        db.commit()
        db.refresh(alarm)
        return alarm