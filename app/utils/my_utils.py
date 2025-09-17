import base64
import datetime
import cv2
import pytz


def get_now():
    return datetime.datetime.now(pytz.timezone('Asia/Shanghai'))

# 将图像编码为JPEG格式
def get_frame_base64(annotated_frame):
    _, buffer = cv2.imencode('.jpg', annotated_frame)
    frame_bytes = buffer.tobytes()
    frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
    return  frame_base64
