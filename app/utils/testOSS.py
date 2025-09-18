import oss2
from dotenv import load_dotenv
import os
import uuid
import datetime

load_dotenv()

# 阿里云OSS配置
OSS_ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID')
OSS_ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET')
OSS_BUCKET_NAME = os.getenv('ALIYUN_OSS_BUCKET_NAME')
OSS_ENDPOINT = os.getenv('ALIYUN_OSS_ENDPOINT')

def upload_img_to_OSS(content, object_key, access_key_id, access_key_secret, bucket_name, endpoint):
    """
    上传图片到阿里云OSS

    参数:
    content: 图片内容(bytes)
    object_key: 上传后的文件名
    access_key_id: 阿里云AccessKey ID
    access_key_secret: 阿里云AccessKey Secret
    bucket_name: OSS bucket名称
    endpoint: OSS endpoint

    返回:
    文件的URL
    """
    # 创建认证对象
    auth = oss2.Auth(access_key_id, access_key_secret)

    # 创建Bucket对象
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    # 上传文件
    bucket.put_object(object_key, content)

    # 构造文件URL，使用标准的URL格式
    file_url = f"https://{bucket_name}.{endpoint.replace('http://', '').replace('https://', '')}/{object_key}"

    return file_url

def generate_unique_object_name(original_path):
    """
    从原始文件路径生成唯一的OSS文件名，按年/月/日层级存储

    参数:
    original_path: 原始文件路径

    返回:
    唯一的OSS文件名，格式：年/月/日/UUID.扩展名
    """
    # 获取文件扩展名
    ext = os.path.splitext(original_path)[1]

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

if __name__ == '__main__':
    # 读取本地图片文件，获取它的字节数组
    image_path = r"D:\壁纸\桌面壁纸\wallhaven-k7o551.jpg"
    with open(image_path, 'rb') as f:
        print(f'读取图片文件成功！file_path={f.name}')
        img_bytes = f.read()
        # 使用生成的唯一文件名而不是原始路径
        object_name = generate_unique_object_name(image_path)
        # 示例用法
        url = upload_img_to_OSS(
            img_bytes,
            object_name,
            OSS_ACCESS_KEY_ID,
            OSS_ACCESS_KEY_SECRET,
            OSS_BUCKET_NAME,
            OSS_ENDPOINT
        )
        print(f'上传图片成功！oss_file_name={object_name}, url={url}')
