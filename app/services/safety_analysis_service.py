import os
import threading
import time
from typing import Literal, Dict
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from torchgen.api.python import return_type_str_pyi

from app.JSON_schemas.Result_pydantic import Result
from app.crud.alarm_crud import update_alarm_end_time, create_alarm
from app.crud.camera_crud import get_camera_info
from app.objects.alarm_case import AlarmCase
from app.objects.alarm_case_tracker import DebouncedAlarmCaseTracker
from app.services.detection_service import DetectionService
from app.services.storage_service import StorageService
from app.services.alarm_broadcast_service import sync_broadcast_alarm
from app.utils.my_utils import get_now
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建线程池用于处理I/O操作
io_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="IO_Worker")


# -------------------------- 安防监控服务 --------------------------
class SafetyAnalysisService:
    # 全局线程管理
    active_threads: Dict[str, threading.Thread] = {}
    thread_stop_flags: Dict[str, bool] = {}

    # 全局告警跟踪器实例
    alarm_tracker = DebouncedAlarmCaseTracker()

    # -------------------------- RTSP视频流安防检测 --------------------------
    @classmethod
    def _safety_analysis_loop(cls, camera_id: int, rtsp_url: str | int, analysis_mode: Literal[1, 2, 3, 4], db: Session):
        logger.info(f"安防分析线程已启动，开始检测监控摄像头（id={camera_id}），线程名：{threading.current_thread().name}）")
        thread_name = f"安防检测- 摄像头ID: {camera_id}, 分析模式: {AlarmCase.descs[analysis_mode-2]}"
        frame_count = 0

        try:
            model = DetectionService.model
            results = model(rtsp_url, imgsz=640, stream=True, vid_stride=3, save=True,
                            project="detection_results", name=f"摄像头{camera_id} 分析模式{analysis_mode}",
                            verbose=True)
            for r in results:
                frame_count += 1
                # 当frame_count达到int最大值后自动归0，防止整数溢出
                if frame_count == 2147483647:  # 32位有符号整数最大值
                    frame_count = 0
                    logger.info(f"摄像头 {camera_id} 的帧计数器已重置")

                # 检查停止信号（优先判断，确保及时退出）
                if cls.thread_stop_flags.get(thread_name, True):
                    logger.info(f"收到停止信号，停止摄像头 {camera_id}的安防分析")
                    break

                # 该帧中探测出来的告警场景,默认是三种告警场景都没有出现
                alarm_cases: Dict[str, bool] = {"安全规范": False, "区域入侵": False, "火警": False}
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
                        alarm_cases['安全规范'] = True
                    if person_num > 0:
                        alarm_cases['区域入侵'] = True
                    if fire_presence and smoke_presence:
                        alarm_cases['火警'] = True
                elif analysis_mode == 2:
                    if person_num > 0 and (helmet_num < person_num or reflective_vest_num < person_num):
                        alarm_cases['安全规范'] = True
                elif analysis_mode == 3:
                    if person_num > 0:
                        alarm_cases['区域入侵'] = True
                elif analysis_mode == 4:
                    if fire_presence and smoke_presence:
                        alarm_cases['火警'] = True

                # 告警状态跟踪(如果只是关注单个告警场景，则只跟踪该告警场景；如果关注3个告警场景，则跟踪3个告警场景)
                if analysis_mode >= 2:
                    alarm_type = analysis_mode - 2
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
                    for alarm_case_desc, alarm_case_detected in alarm_cases.items():
                        alarm_type = -1
                        if alarm_case_desc == "安全规范":
                            alarm_type = 0
                        elif alarm_case_desc == "区域入侵":
                            alarm_type = 1
                        elif alarm_case_desc == "火警":
                            alarm_type = 2
                        alarm_case_source = f"{camera_id}_{alarm_type}"
                        state_result = cls.alarm_tracker.update_state(alarm_case_source, alarm_case_detected)
                        # 处理本次状态分析结果
                        cls.handle_state_result(state_result, camera_id, alarm_type, alarm_case_source, r, db)

        except Exception as e:
            logger.error(f"摄像头 {camera_id} 监控异常：{str(e)}")
        finally:
            # 从线程管理中移除
            if thread_name in cls.active_threads:
                del cls.active_threads[thread_name]
            if thread_name in cls.thread_stop_flags:
                del cls.thread_stop_flags[thread_name]
            logger.info(f"摄像头 {camera_id} 安防分析已停止：处理帧 {frame_count} 帧")

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
            """""
            # 从数据库中读取摄像头信息
            camera_info= get_camera_info(db, camera_id)
            if not camera_info:
                return Result.ERROR(f"未找到摄像头 {camera_id} 的信息")
            rtsp_url= camera_info.rtsp_url
            analysis_mode = camera_info.analysis_mode
            """
            # current_script_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # rtsp_url = os.path.join(current_script_parent_dir, "test_videos", "all_helmet_but_none_vest.mp4")
            rtsp_url = r"D:\D盘桌面\模型测试\all_helmet_but_none_vest.mp4"
            analysis_mode = 2
            logger.info(f"开启安防分析，视频流：{rtsp_url}, 分析模式：{AlarmCase.descs[analysis_mode-2]}")

            thread_name = cls.start_thread(camera_id, rtsp_url, analysis_mode, db)

            result_data = {
                "camera_id": camera_id,
                "rtsp_url": rtsp_url,
                "analysis_mode": analysis_mode,
                "started_thread": thread_name
            }
            return Result.SUCCESS(result_data, f"已成功启动摄像头 {camera_id} 的监控服务")

        except Exception as e:
            logger.error(f"启动监控失败: {str(e)}")
            return Result.ERROR(f"启动监控失败: {str(e)}")

    @classmethod
    def stop_thread(cls, camera_id, t_mode):
        t_name = f"安防检测- 摄像头ID: {camera_id}, 分析模式: {AlarmCase.descs[t_mode-2]}"
        cls.thread_stop_flags[t_name] = True
        if t_name in cls.active_threads:
            del cls.active_threads[t_name]
        logger.info(f"发送停止信号到线程: {t_name}")
        return t_name

    @classmethod
    def stop_safety_analysis(cls, camera_id: str, db: Session) -> Result:
        try:
            camera_id = int(camera_id)
            camera_info = get_camera_info(db, camera_id)
            if not camera_info:
                return Result.ERROR(f"未找到ID为 {camera_id} 的摄像头信息")

            analysis_mode = camera_info.analysis_mode or 2

            thread_name = cls.stop_thread(camera_id, analysis_mode)

            result_data = {
                "camera_id": camera_id,
                "analysis_mode": analysis_mode,
                "stopped_thread": thread_name
            }
            return Result.SUCCESS(result_data, f"已发送停止监控信号: 摄像头 {camera_id}")

        except Exception as e:
            logger.error(f"停止监控失败: {str(e)}")
            return Result.ERROR(f"停止监控失败: {str(e)}")

    @classmethod
    def handle_state_result(cls, state_result, camera_id, alarm_type, alarm_case_source, r, db):
        state_changed = state_result["state_changed"]
        change_type = state_result["change_type"]
        if state_changed:
            if change_type == "normal_to_violation":
                # 完全异步处理：保存截图、创建告警、广播告警都在后台线程执行
                def process_alarm_async():
                    try:
                        # 保存截图到云OSS并获取URL
                        snapshot_url = StorageService.upload_alarm_snapshot(r.plot(), camera_id)
                        logger.info(f"已经保存告警截图到云OSS，访问URL: {snapshot_url}")

                        # 创建告警记录
                        alarm = create_alarm(db, camera_id, alarm_type, 0, get_now(), snapshot_url)
                        logger.info(f"已经为摄像头（ID： {camera_id}）创建告警（Alarm ID：{alarm.alarm_id}，告警类型：{AlarmCase.descs[alarm_type]}）")

                        # 绑定告警ID到跟踪器
                        cls.alarm_tracker.bind_alarm_id(alarm_case_source, alarm.alarm_id)
                        logger.info(f"已经绑定告警(Alarm ID:{alarm.alarm_id}) 到告警场景状态:{cls.alarm_tracker.alarm_case_states[alarm_case_source]}")

                        # 广播告警
                        sync_broadcast_alarm(alarm)
                    except Exception as e:
                        logger.error(f"处理告警时发生错误: {e}")

                # 提交到后台线程执行，不阻塞主线程
                io_executor.submit(process_alarm_async)

            elif change_type == "violation_to_normal":
                # 异步更新告警结束时间（数据库操作）
                def update_alarm_async():
                    try:
                        update_alarm_end_time(
                            db=db,
                            alarm_id=state_result["alarm_id"],
                            alarm_end_time=get_now()
                        )
                        logger.info(f"摄像头 {camera_id} 更新告警（ID：{state_result['alarm_id']}）")
                    except Exception as e:
                        logger.error(f"更新告警结束时间时发生错误: {e}")

                io_executor.submit(update_alarm_async)
