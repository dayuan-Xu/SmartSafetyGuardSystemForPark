import cv2
import time
import threading

from app.JSON_schemas.Result_pydantic import Result
from app.crud.camera_crud import get_camera_info


# 视频流采集服务（视频帧获取服务）
class VideoCaptureService:
    def __init__(self, rtsp_url:str|int):
        self.rtsp_url = rtsp_url
        self.cap = None
        self.running = False
        self.thread = None
        self.frame = None         # 最新一帧图像
        self.frame_timestamp = 0  # 最新帧的时间戳
        self.lock = threading.Lock()
        self.frame_timeout = 10.0  # 帧超时时间（秒）

    def start(self):
        """启动视频流采集线程"""
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        time.sleep(3)  # 等待线程启动
        return self.is_connected()

    def _capture_loop(self):
        """子线程的内部循环：持续获取视频帧"""
        consecutive_failures = 0 # 连续失败次数(视频流打开/读帧)
        max_consecutive_failures = 10  # 最大连续失败次数
        file_replay_count = 0  # 文件重播次数

        while self.running:
            # 确保视频流已打开，添加了重试机制
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.rtsp_url)
                if self.cap.isOpened():
                    consecutive_failures = 0 # 成功连接，重置失败计数
                    # total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) # 获取视频总帧数（用于调试）
                    print(f"视频流成功打开")
                else:
                    print(f"无法打开视频流: {self.rtsp_url}")
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        print(f"达到最大连续失败次数 ({max_consecutive_failures})，停止尝试连接: {self.rtsp_url}")
                        break
                    time.sleep(2)
                    continue

            ret, frame = self.cap.read()
            if ret:# 成功读取，重置失败计数, 更新帧、时间戳
                consecutive_failures = 0
                with self.lock:
                    self.frame = frame
                    self.frame_timestamp = time.time()
            else: # 读取失败
                if not self.rtsp_url.startswith('rtsp'): # 如果是文件播放，则最多再尝试读帧10次
                    consecutive_failures += 1

                    current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) if self.cap else 0
                    total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) if self.cap else 0
                    print(f"视频新帧读取失败 - 当前帧: {current_frame}, 总帧数: {total_frames}")

                    if current_frame >= total_frames > 0:# 如果是视频文件播放完毕
                        file_replay_count += 1
                        if file_replay_count > 1:
                            print(f"视频文件播放完毕，已尝试播放 {file_replay_count-1} 次，不再尝试播放: {self.rtsp_url}")
                            break
                        print(f"视频文件播放完毕，断开当前连接，重新连接，开始重播 (第 {file_replay_count} 次): {self.rtsp_url}")
                        self.cap.release()
                        self.cap = None
                        consecutive_failures = 0  # 重置失败计数
                        continue
                    else:
                        if consecutive_failures >= max_consecutive_failures:
                            print(f"视频文件并非到了最后一帧（播放完毕），但读帧连续失败了{max_consecutive_failures}次，停止尝试读取: {self.rtsp_url}")
                            break


                else:# 对于RTSP流，读取失败可能是暂时的问题，则只检查是否超过阈值（10s都没有读取到新的一帧）
                    if self.is_frame_stale():
                        print(f"RTSP流超时了 {time.time()-self.frame_timestamp:.2f}s > {self.frame_timeout}s（超时阈值），停止尝试读取: {self.rtsp_url}")
                        break

        # 释放资源
        if self.cap and self.cap.isOpened():
            self.cap.release()

        # 标记视频读取服务实例停止运行
        self.running = False

        print(f"视频采集服务停止运行: {self.rtsp_url}")


    def get_frame_with_timestamp(self):
        """获取最新一帧图像和时间戳"""
        with self.lock:
            # 返回最新帧（注意：这里的“最新帧”只是成功读取的最后一帧，不一定是摄像头刚刚拍摄生成的帧）
            return self.frame.copy(), self.frame_timestamp


    def is_connected(self):
        """检查是否成功连接到视频流"""
        return self.cap is not None and self.cap.isOpened()


    def is_frame_stale(self):
        """检查帧是否过期（长时间未更新）"""
        with self.lock:
            return time.time() - self.frame_timestamp > self.frame_timeout

    def stop(self):
        """停止视频流采集"""
        self.running = False
        # 等待循环读帧的线程结束
        if self.thread and self.thread.is_alive():
            self.thread.join()

    @classmethod
    def test_camera_connection(cls, camera_id, db):
        """
        测试目标摄像头视频流rtsp_url能否打开

        Args:
            camera_id: 摄像头ID
            db: 数据库会话

        Returns:
            Result[bool]: 测试结果
        """
        try:
            camera_info = get_camera_info(db, camera_id)

            if not camera_info:
                return Result.ERROR(f"未找到ID为 {camera_id} 的摄像头信息")

            # 尝试连接视频流
            cap = cv2.VideoCapture(camera_info.rtsp_url)
            if cap.isOpened():
                cap.release()
                return Result.SUCCESS(True, "连接成功")
            else:
                return Result.ERROR("连接失败")

        except Exception as e:
            return Result.ERROR(f"测试连接时发生错误: {str(e)}")
