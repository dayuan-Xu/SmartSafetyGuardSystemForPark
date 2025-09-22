import base64
import os
from datetime import datetime
import cv2
from dotenv import load_dotenv

from app.utils.my_utils import upload_file_on_OSS, get_now_str, generate_unique_object_name

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
    def upload_alarm_snapshot(annotated_frame, camera_id):
        """上传告警截图到云存储"""
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        img_name = f"{camera_id}_{get_now_str()}.jpg"
        object_key= generate_unique_object_name(img_name)
        file_url = upload_file_on_OSS(frame_bytes, object_key)
        return file_url

    @classmethod
    def upload_alarm_attachment(cls, file_content: str, file_extension: str) -> str:
        """
        上传告警处理附件到云存储并返回URL

        参数:
        file_content: Base64编码的文件内容
        file_extension: 文件扩展名，例如 ".jpg", ".png"

        返回:
        文件的URL
        """
        # 解码Base64内容
        file_bytes = base64.b64decode(file_content)

        # 生成文件名
        filename = f"attachment_{get_now_str()}{file_extension}"
        object_key = generate_unique_object_name(filename)

        # 上传到OSS并返回URL
        file_url = upload_file_on_OSS(file_bytes, object_key)
        return file_url
