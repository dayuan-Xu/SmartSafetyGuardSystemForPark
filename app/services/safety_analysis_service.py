import threading
from pathlib import Path
from typing import Literal, Dict
import cv2
from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.crud.alarm_crud import update_alarm_end_time, create_alarm
from app.crud.camera_crud import get_camera_info
from app.objects.alarm_case import AlarmCase
from app.objects.alarm_case_tracker import DebouncedAlarmCaseTracker
from app.services.alarm_broadcast_service import sync_broadcast_alarm
from app.services.detection_service import DetectionService
from app.services.storage_service import StorageService
from app.services.thread_pool_manager import executor as io_executor
from app.utils.logger import get_logger
from app.utils.oss_utils import get_now

logger = get_logger()


# -------------------------- 安防监控服务 --------------------------
class SafetyAnalysisService:
    # 全局线程管理
    active_threads: Dict[str, threading.Thread] = {}
    thread_stop_flags: Dict[str, bool] = {}

    # 全局告警跟踪器实例
    alarm_tracker = DebouncedAlarmCaseTracker()

    # 分析模式编码对应描述
    analysis_mode_descs = {
        1: "全部(安全规范+区域入侵+火警)",
        2: "安全规范(安全帽、反光衣穿戴检测)",
        3: "区域入侵(人体、车辆检测)",
        4: "火警(火焰、烟雾检测)"
    }

    # -------------------------- RTSP视频流安防检测 --------------------------
    @classmethod
    def _safety_analysis_loop(cls, camera_id: int, rtsp_url: str | int, analysis_mode: Literal[1, 2, 3, 4], db: Session):
        logger.info(f"安防分析线程已启动，线程名：{threading.current_thread().name}）")
        thread_name = f"安防检测- 摄像头ID: {camera_id}, 分析模式: {AlarmCase.descs[analysis_mode-2]}"
        frame_count = 0

        try:
            # 认为该模型能够检测出所有告警场景中的所有目标类别的对象
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

    @classmethod
    def _safety_analysis_loop_v2(cls, camera_id: int, rtsp_url: str | int, analysis_mode: Literal[1, 2, 3, 4], db: Session):
        thread_name=threading.current_thread().name
        logger.info(f"安防分析线程已启动，线程名：{thread_name}")
        frame_count = 0
        cap = cv2.VideoCapture(rtsp_url)
        try:
            while cap.isOpened():
                # 检查停止信号（优先判断，确保及时退出）
                if cls.thread_stop_flags.get(thread_name, True):
                    logger.info(f"收到停止信号，停止{thread_name}")
                    break
                ret, frame=cap.read()
                if ret:
                    frame_count += 1
                    if frame_count==2147483647:
                        frame_count = 0
                        logger.info("已处理2147483647帧，现重置frame_count为0")

                    if analysis_mode>=2: # 只分析一种告警场景
                        alarm_type = analysis_mode - 2
                        alarm_case_detected,annotated_frames = DetectionService.detect_alarm_case(frame,alarm_type)
                        if alarm_case_detected is not None:
                            alarm_case_source = f"{camera_id}_{alarm_type}"
                            state_result = cls.alarm_tracker.update_state(alarm_case_source, alarm_case_detected)
                            # 处理本次状态分析结果
                            cls.handle_state_result_v2(state_result, camera_id, alarm_type, alarm_case_source, annotated_frames, db)
                    elif analysis_mode==1: # 分析3种告警场景
                        for analysis_mode_temp in range(2,5):
                            alarm_type = analysis_mode_temp - 2
                            alarm_case_detected, annotated_frames = DetectionService.detect_alarm_case(frame, alarm_type)
                            if alarm_case_detected is not None:
                                alarm_case_source = f"{camera_id}_{alarm_type}"
                                state_result = cls.alarm_tracker.update_state(alarm_case_source, alarm_case_detected)
                                # 处理本次状态分析结果
                                cls.handle_state_result_v2(state_result, camera_id, alarm_type, alarm_case_source, annotated_frames, db)
                else:
                    logger.info(f"{thread_name}本次获取视频帧失败")

        except Exception as e:
            logger.error(f"{thread_name} 内出现异常：{str(e)}")
        finally:
            # 释放资源
            cap.release()
            # 从线程管理中移除
            if thread_name in cls.active_threads:
                del cls.active_threads[thread_name]
            if thread_name in cls.thread_stop_flags:
                del cls.thread_stop_flags[thread_name]
            logger.info(f"{thread_name} 已停止：处理帧 {frame_count} 帧")


    # -------------------------- 安防检测循环启停方法 --------------------------
    @classmethod
    def get_thread_name(cls, camera_id, analysis_mode):
        return f"安防分析线程- 摄像头ID: {camera_id}, 分析模式: {cls.analysis_mode_descs[analysis_mode]}"

    @classmethod
    def start_thread(cls, camera_id, rtsp_url, t_mode, db):
        t_name = cls.get_thread_name(camera_id, t_mode)
        cls.thread_stop_flags[t_name] = False

        thread = threading.Thread(
            target=cls._safety_analysis_loop_v2,
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
            # 从数据库中读取摄像头信息
            camera_info_result = get_camera_info(db, camera_id)
            if not camera_info_result:
                return Result.ERROR(f"未找到ID为 {camera_id} 的摄像头信息")
            
            # 从联表查询结果中提取摄像头信息
            camera_info = camera_info_result[0]  # CameraInfoDB instance

            analysis_mode = camera_info.analysis_mode or 2

            # 测试时，服务器本地视频充当实时视频流
            project_root = Path(__file__).parent.parent.parent
            if analysis_mode == 4:
                rtsp_url = project_root / 'app' / 'test_videos' / "fire_smoke.mp4"
            elif  analysis_mode == 3:
                rtsp_url = project_root / 'app' / 'test_videos' / "person_vehicle.mp4"
            elif analysis_mode == 2:
                rtsp_url = project_root / 'app' / 'test_videos' / "helmet_vest.mp4"
            elif analysis_mode == 1:
                rtsp_url = project_root / 'app' / 'test_videos' / "all.mp4"
            else:
                return Result.ERROR(f"当前摄像头: {camera_info.camera_name} 未指定分析模式，无法开启实时分析!")

            logger.info(f"开启安防分析，视频流URL：{rtsp_url}, 分析模式：{cls.analysis_mode_descs[analysis_mode]}")

            # 启动分析线程
            if rtsp_url is None:
                return Result.ERROR(f"未找到摄像头: {camera_info.camera_name} 的视频流URL，无法开启实时分析")
            else:
                thread_name = cls.start_thread(camera_id, rtsp_url, analysis_mode, db)

                result_data = {
                    "camera_id": camera_id,
                    "rtsp_url": rtsp_url,
                    "analysis_mode": analysis_mode,
                    "started_thread": thread_name
                }
                return Result.SUCCESS(result_data, f"已成功启动 {camera_info.camera_name} 的监控服务")

        except Exception as e:
            logger.error(f"启动监控失败: {str(e)}")
            return Result.ERROR(f"启动监控失败: {str(e)}")

    @classmethod
    def stop_thread(cls, camera_id, t_mode):
        t_name = cls.get_thread_name(camera_id, t_mode)
        logger.info(f"当前活动线程: {list(cls.active_threads.keys())}")
        logger.info(f"尝试停止线程: {t_name}")
        cls.thread_stop_flags[t_name] = True
        if t_name in cls.active_threads:
            del cls.active_threads[t_name]
        logger.info(f"成功发送停止信号到线程: {t_name}")
        return t_name

    @classmethod
    def stop_safety_analysis(cls, camera_id: str, db: Session) -> Result:
        try:
            camera_id = int(camera_id)
            camera_info_result = get_camera_info(db, camera_id)
            if not camera_info_result:
                return Result.ERROR(f"未找到ID为 {camera_id} 的摄像头信息")
            
            # 从联表查询结果中提取摄像头信息
            camera_info = camera_info_result[0]  # CameraInfoDB instance

            analysis_mode = camera_info.analysis_mode or 2

            thread_name = cls.stop_thread(camera_id, analysis_mode)

            result_data = {
                "camera_id": camera_id,
                "analysis_mode": analysis_mode,
                "stopped_thread": thread_name
            }
            return Result.SUCCESS(result_data, f"已发送停止信号到 {camera_info.camera_name}")

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

    @classmethod
    def handle_state_result_v2(cls, state_result, camera_id, alarm_type, alarm_case_source, annotated_frames, db):
        state_changed = state_result["state_changed"]
        change_type = state_result["change_type"]
        if state_changed:
            if change_type == "normal_to_violation":
                # 完全异步处理：保存截图、创建告警、广播告警都在后台线程执行
                def process_alarm_async():
                    try:
                        snapshot_urls="" # 包含本次告警的所有经过标注的帧的url
                        for i,annotated_frame in enumerate(annotated_frames):
                            # 保存截图到云OSS并获取URL
                            snapshot_url = StorageService.upload_alarm_snapshot(annotated_frame, camera_id)
                            snapshot_urls+=snapshot_url
                            if i > 0:
                                snapshot_urls+=','
                            logger.info(f"已经保存告警截图到云OSS，访问URL: {snapshot_url}")

                        # 创建告警记录
                        alarm = create_alarm(db, camera_id, alarm_type, 0, get_now(), snapshot_urls)
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
