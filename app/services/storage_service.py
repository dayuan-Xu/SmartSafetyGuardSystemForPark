import os
from datetime import datetime
import cv2
from dotenv import load_dotenv

from app.utils.my_utils import upload_img_to_OSS, get_now_str, generate_unique_object_name

load_dotenv()
SNAPSHOT_PATH = os.getenv('SNAPSHOT_PATH')

# 确保截图目录存在
os.makedirs(SNAPSHOT_PATH, exist_ok=True)


class StorageService:
    @staticmethod
    def save_alarm_snapshot_locally(frame, camera_id):
        """保存告警截图并返回存储路径"""
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{camera_id}_{timestamp}.jpg"
        filepath = os.path.join(SNAPSHOT_PATH, filename)

        # 保存图像
        cv2.imwrite(filepath, frame)
        return filepath

    @staticmethod
    def upload_alarm_snapshot(frame, camera_id):
        """上传告警截图到云存储"""
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        img_name = f"{camera_id}_{get_now_str()}.jpg"
        object_key= generate_unique_object_name(img_name)
        file_url = upload_img_to_OSS(frame_bytes, object_key)
        return file_url
