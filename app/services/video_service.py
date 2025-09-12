import cv2
import time
import threading
from datetime import datetime


class VideoCaptureService:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = None
        self.running = False
        self.last_frame = None
        self.lock = threading.Lock()

    def start(self):
        """启动视频流采集线程"""
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        time.sleep(1)  # 等待线程启动
        return self.is_connected()

    def _capture_loop(self):
        """内部循环：持续获取视频帧"""
        self.cap = cv2.VideoCapture(self.rtsp_url)

        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.last_frame = frame
            else:
                time.sleep(0.1)

        # 释放资源
        if self.cap:
            self.cap.release()

    def get_frame(self):
        """获取最新一帧图像"""
        with self.lock:
            return self.last_frame.copy() if self.last_frame is not None else None

    def is_connected(self):
        """检查是否连接成功"""
        return self.cap is not None and self.cap.isOpened()

    def stop(self):
        """停止视频流采集"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join()