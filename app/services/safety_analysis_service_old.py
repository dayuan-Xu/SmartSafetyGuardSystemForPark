import asyncio
import os
import threading
import time
from typing import Literal, Dict, List
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.crud.alarm_crud import update_alarm_end_time, create_alarm
from app.crud.camera_crud import get_camera_info
from app.objects.alarm_case import AlarmCase
from app.objects.alarm_case_tracker import DebouncedAlarmCaseTracker
from app.services.detection_service import DetectionService
from app.services.storage_service import StorageService
from app.utils.oss_utils import get_now


# -------------------------- 1. WebSocket管理器，提供连接、断开连接、发送个人消息和广播消息的功能 --------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:  # 增加存在性判断，避免KeyError
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        """优化：批量处理连接，失败后及时移除无效连接"""
        valid_connections = []
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
                valid_connections.append(conn)  # 仅保留发送成功的连接
            except Exception:
                continue
        self.active_connections = valid_connections  # 更新有效连接列表

# 创建全局WebSocket管理器
manager = ConnectionManager()

# -------------------------- 2. 全局异步广播任务处理（使用独立线程运行事件循环，避免与FastAPI主线程冲突） --------------------------
# 1. 创建独立的asyncio事件循环，专门处理WebSocket广播（避免与FastAPI主循环冲突）
broadcast_loop = asyncio.new_event_loop()
# 2. 启动事件循环的守护线程（后台运行，不阻塞主程序退出）
broadcast_thread = threading.Thread(
    target=broadcast_loop.run_forever,
    daemon=True,
    name="WebSocket-Broadcast-Loop"
)
broadcast_thread.start()

async def _async_broadcast_alarm(alarm):
    """内部异步广播告警函数（供事件循环调用）"""
    alarm_dict = {
        "alarm_id": alarm.alarm_id,
        "camera_id": alarm.camera_id,
        "alarm_type": alarm.alarm_type,
        "alarm_status": alarm.alarm_status,
        "alarm_time": alarm.alarm_time.isoformat() if alarm.alarm_time else None,
        "snapshot_url": alarm.snapshot_url,
    }
    await manager.broadcast(alarm_dict)

def sync_broadcast_alarm(alarm):
    """同步接口：将告警广播任务提交到全局事件循环（线程安全）"""
    asyncio.run_coroutine_threadsafe(
        _async_broadcast_alarm(alarm),
        loop=broadcast_loop
    )

# -------------------------- 3. 安防监控服务 --------------------------
class SafetyMonitorService:
    # 全局线程管理
    active_threads: Dict[str, threading.Thread] = {}
    thread_stop_flags: Dict[str, bool] = {}

    # 全局告警跟踪器实例
    alarm_tracker = DebouncedAlarmCaseTracker()

       # -------------------------- RTSP视频流安防检测 --------------------------
    @classmethod
    def _safety_analysis_loop(cls, camera_id: int, rtsp_url: str | int, analysis_mode: Literal[1, 2, 3, 4], db: Session):
        print(f"开始对监控摄像头进行安防检测 {camera_id}（线程：{threading.current_thread().name}）")
        thread_name = f"安防检测- 摄像头ID: {camera_id}, 分析模式: {AlarmCase.descs[analysis_mode-2]}"
        frame_count = 0

        try:
            model=DetectionService.model
            results=model(rtsp_url, imgsz=640, stream= True, vid_stride=3, save=True, project="detection_results", name=f"摄像头{camera_id} 分析模式{analysis_mode}", verbose=False)
            for r in results:
                frame_count += 1
                # 检查停止信号（优先判断，确保及时退出）
                if cls.thread_stop_flags.get(thread_name, True):
                    print(f"收到停止信号，停止摄像头 {camera_id}的安防分析")
                    break

                # 该帧中探测出来的告警场景,默认是三种告警场景都没有出现
                alarm_cases:Dict[str, bool] = {"安全规范":False, "区域入侵":False, "火警":False}
                person_num = 0
                helmet_num = 0
                reflective_vest_num = 0
                fire_presence = False
                smoke_presence = False
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    # 是人
                    if class_id == DetectionService.person_class_id:
                        person_num += 1
                    # 是戴在人头上的安全帽
                    elif class_id == DetectionService.helmet_class_id:
                        helmet_num += 1
                    # 是反射衣
                    elif class_id == DetectionService.reflective_vest_class_id:
                        reflective_vest_num += 1
                    # 是火焰
                    elif class_id == DetectionService.fire_class_id:
                        fire_presence = True
                    # 是烟雾
                    elif class_id == DetectionService.smoke_class_id:
                        smoke_presence = True
                # 构造要返回的告警场景列表
                if analysis_mode == 1:
                    if person_num > 0 and (helmet_num < person_num or reflective_vest_num < person_num):
                        alarm_cases['安全规范']= True
                    if person_num > 0:
                        alarm_cases['区域入侵']= True
                    if fire_presence and smoke_presence:
                        alarm_cases['火警']= True
                elif analysis_mode == 2:
                    if person_num > 0 and (helmet_num < person_num or reflective_vest_num < person_num):
                        alarm_cases['安全规范']= True
                elif analysis_mode == 3:
                    if person_num > 0:
                        alarm_cases['区域入侵']= True
                elif analysis_mode == 4:
                    if fire_presence and smoke_presence:
                        alarm_cases['火警'] = True

                # 告警状态跟踪(如果只是关注单个告警场景，则只跟踪该告警场景；如果关注3个告警场景，则跟踪3个告警场景)
                if analysis_mode >=2:
                    alarm_type=analysis_mode-2
                    alarm_case_source = f"{camera_id}_{alarm_type}"
                    target_alarm_case_desc = AlarmCase.descs[alarm_type]
                    alarm_case_detected = alarm_cases[target_alarm_case_desc]
                    state_result = cls.alarm_tracker.update_state(alarm_case_source, alarm_case_detected)
                    # 处理本次状态分析结果
                    cls.handle_state_result(state_result, camera_id, alarm_type, alarm_case_source, r, db)
                    # 处理下一个探测结果
                    continue
                else:
                    # 如果关注3个告警场景，则需要分别跟踪
                    for alarm_case_desc,alarm_case_detected in alarm_cases.items():
                        alarm_type=-1
                        if alarm_case_desc== "安全规范":
                            alarm_type=0
                        elif alarm_case_desc== "区域入侵":
                            alarm_type=1
                        elif alarm_case_desc== "火警":
                            alarm_type=2
                        alarm_case_source=f"{camera_id}_{alarm_type}"
                        state_result = cls.alarm_tracker.update_state(alarm_case_source, alarm_case_detected)
                        # 处理本次状态分析结果
                        cls.handle_state_result(state_result, camera_id, alarm_type, alarm_case_source, r, db)

        except Exception as e:
            print(f"摄像头 {camera_id} 监控异常：{str(e)}")
        finally:
            # 从线程管理中移除
            if thread_name in cls.active_threads:
                del cls.active_threads[thread_name]
            if thread_name in cls.thread_stop_flags:
                del cls.thread_stop_flags[thread_name]
            print(f"摄像头 {camera_id} 安防分析已停止：处理帧 {frame_count} 帧")

    # -------------------------- 安防检测循环启停方法 --------------------------
    @classmethod
    def start_thread(cls, camera_id, rtsp_url, t_mode, db):
        t_name = f"安防检测- 摄像头ID: {camera_id}, 分析模式: {AlarmCase.descs[t_mode-2]}"
        cls.thread_stop_flags[t_name] = False

        thread = threading.Thread(
            target=cls._safety_analysis_loop,
            args=(camera_id, rtsp_url, t_mode, db),
            daemon=True,
            name=t_name
        )

        cls.active_threads[t_name] = thread
        thread.start()
        return t_name

    @classmethod
    def start_safety_analysis(cls, camera_id: str, db: Session) -> Result:
        try:
            camera_id = int(camera_id)
            current_script_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rtsp_url = os.path.join(current_script_parent_dir, "test_videos", "all_helmet_but_none_vest.mp4")
            print("开启监控视频流：", rtsp_url)
            analysis_mode = 3

            thread_name = cls.start_thread(camera_id, rtsp_url, analysis_mode, db)

            result_data = {
                "camera_id": camera_id,
                "rtsp_url": rtsp_url,
                "analysis_mode": analysis_mode,
                "started_thread": thread_name
            }
            return Result.SUCCESS(result_data, f"已成功启动摄像头 {camera_id} 的监控服务")

        except Exception as e:
            return Result.ERROR(f"启动监控失败: {str(e)}")

    @classmethod
    def stop_thread(cls, camera_id, t_mode):
        t_name = f"安防检测- 摄像头ID: {camera_id}, 分析模式: {AlarmCase.descs[t_mode-2]}"
        cls.thread_stop_flags[t_name] = True
        if t_name in cls.active_threads:
            del cls.active_threads[t_name]
        return t_name

    @classmethod
    def stop_safety_analysis(cls, camera_id: str, db: Session) -> Result:
        try:
            camera_id = int(camera_id)
            camera_info_result = get_camera_info(db, camera_id)
            if not camera_info_result:
                return Result.ERROR(f"未找到ID为 {camera_id} 的摄像头信息")

            # 从联表查询结果中提取摄像头信息
            camera_info = camera_info_result.CameraInfoDB

            analysis_mode = camera_info.analysis_mode or 2

            thread_name = cls.stop_thread(camera_id, analysis_mode)

            result_data = {
                "camera_id": camera_id,
                "analysis_mode": analysis_mode,
                "stopped_thread": thread_name
            }
            return Result.SUCCESS(result_data, f"已发送停止监控信号: 摄像头 {camera_id}")

        except Exception as e:
            return Result.ERROR(f"停止监控失败: {str(e)}")

    @classmethod
    def handle_state_result(cls, state_result, camera_id, alarm_type, alarm_case_source, r, db):
        state_changed = state_result["state_changed"]
        change_type = state_result["change_type"]
        if state_changed:
            if change_type == "normal_to_violation":
                # 保存截图（轻量级I/O，可根据需求提交到线程池）
                snapshot_path = StorageService.save_snapshot(r.plot(), camera_id)
                # 创建告警（数据库操作，若耗时可加线程池）
                alarm=create_alarm(db,camera_id, alarm_type, 0, get_now(), snapshot_path)
                print(f"[{time.ctime()}] 已经为摄像头（ID： {camera_id}）创建告警（Alarm ID：{alarm.alarm_id}）")
                cls.alarm_tracker.bind_alarm_id(alarm_case_source, alarm.alarm_id)
                # 广播告警（非阻塞）
                sync_broadcast_alarm(alarm)

            elif change_type == "violation_to_normal":
                # 更新告警结束时间（数据库操作）
                update_alarm_end_time(
                    db=db,
                    alarm_id=state_result["alarm_id"],
                    alarm_end_time=get_now()
                )
                print(f"摄像头 {camera_id} 更新告警（ID：{state_result['alarm_id']}）")