import os
import cv2
from datetime import datetime
from sqlalchemy.orm import Session
from app.DB_models.alarm_db import AlarmDB
from dotenv import load_dotenv

from app.crud.alarm_crud import create_alarm

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
