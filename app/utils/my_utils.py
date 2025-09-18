import base64
import datetime
import os
import uuid
import cv2
import oss2
import pytz
from pathlib import Path

# 阿里云OSS配置
OSS_ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID')
OSS_ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET')
OSS_BUCKET_NAME = os.getenv('ALIYUN_OSS_BUCKET_NAME')
OSS_ENDPOINT = os.getenv('ALIYUN_OSS_ENDPOINT')

# 获取当前时间（东八区时间）
def get_now():
    return datetime.datetime.now(pytz.timezone('Asia/Shanghai'))

# 获取当前时间字符串
def get_now_str():
    return get_now().strftime("%Y-%m-%d %H:%M:%S")

# 将图像编码为JPEG格式
def get_frame_base64(annotated_frame):
    _, buffer = cv2.imencode('.jpg', annotated_frame)
    frame_bytes = buffer.tobytes()
    frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
    return  frame_base64

def generate_unique_object_name(original_path):
    """
    从原始文件路径生成唯一的OSS文件名，按年/月/日层级存储

    参数:
    original_path: 原始文件路径

    返回:
    唯一的OSS文件名，格式：年/月/日/UUID.扩展名
    """
    # 使用Path获取文件扩展名
    file_path = Path(original_path)
    ext = file_path.suffix

    # 获取当前日期
    now = datetime.datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")

    # 生成UUID
    unique_id = str(uuid.uuid4())

    # 创建层级文件名：年/月/日/+UUID+扩展名
    unique_object_name = f"{year}/{month}/{day}/{unique_id}{ext}"

    return unique_object_name

def upload_img_to_OSS(content, object_key):
    """
    上传图片到阿里云OSS

    参数:
    content: 图片内容(bytes对象)
    object_key: 上传后的文件名
    access_key_id: 阿里云AccessKey ID
    access_key_secret: 阿里云AccessKey Secret
    bucket_name: OSS bucket名称
    endpoint: OSS endpoint

    返回:
    文件的URL
    """
    # 创建认证对象
    auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)

    # 创建Bucket对象
    bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

    # 上传文件
    bucket.put_object(object_key, content)

    # 构造文件URL，使用标准的URL格式
    file_url = f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT.replace('http://', '').replace('https://', '')}/{object_key}"

    return file_url

if __name__ == '__main__':
    print(get_now_str())
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
