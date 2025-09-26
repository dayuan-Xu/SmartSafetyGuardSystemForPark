from pathlib import Path
from ultralytics import YOLO
from app.utils.logger import get_logger

logger = get_logger()
# 模型推理服务
class DetectionService:
    # 使用Path获取项目根目录
    project_root = Path(__file__).parent.parent.parent

    descs = ["安全规范(未戴安全帽、未穿反光衣)", "区域入侵(人)", "火警(火焰、烟雾)"]

    # 告警类型描述+编码，对应AlarmDB中alarm_type字段
    desc_and_code = {"安全规范": 0, "区域入侵": 1, "火警": 2}

    # 加载训练模型（认为该模型能够检测出所有场景中的所有类别的目标）
    model=YOLO(project_root / 'app' / 'models' / 'yolo11s.pt')

    # 人体类别ID
    person_class_id = 0
    # 车辆类别ID
    vehicle_class_id = 1
    # 安全帽类别ID
    helmet_class_id = -1
    # 反光背心
    reflective_vest_class_id = -2
    # 火焰
    fire_class_id = -3
    # 烟雾
    smoke_class_id = -4

    # 置信度阈值
    confidence_threshold = 0.5

    # 构建各个模型文件的路径
    helmet_model_path = project_root / 'app' / 'models' / 'helmet_model.pt'
    vest_model_path = project_root / 'app' / 'models' / 'vest_model.pt'
    person_vehicle_model_path = project_root / 'app' / 'models' / 'yolo11s.pt'
    fire_smoke_model_path = project_root / 'app' / 'models' / 'fire_smoke_model.pt'

    helmet_model = YOLO(helmet_model_path)  # 安全帽检测模型
    vest_model = YOLO(vest_model_path)  # 反光衣检测模型
    person_vehicle_model = YOLO(person_vehicle_model_path)  # 人体车辆检测模型，这里直接使用COCO数据集上预训练的yolo11s模型即可
    fire_smoke_model = YOLO(fire_smoke_model_path)  # 火焰烟雾检测模型

    @classmethod
    def detect_alarm_case(cls,frame, alarm_case_code):
        if alarm_case_code==0:
            # logger.info("本次帧分析的目标告警场景：安全规范（是否佩戴安全帽、是否穿戴反光衣）")

            head_detected=False
            head_class_id=0 # 未戴安全帽的头部在模型训练集中的类别id
            helmet_result=cls.helmet_model(frame,imgsz=640)[0]
            for box in helmet_result.boxes:
                class_id = int(box.cls[0])
                if class_id == head_class_id:
                    head_detected=True

            no_vest_detected=False
            no_vest_class_id=0 # 未穿反光衣在模型训练集中的类别id
            vest_result=cls.vest_model(frame,imgsz=640)[0]
            for box in vest_result.boxes:
                class_id = int(box.cls[0])
                if class_id == no_vest_class_id:
                    no_vest_detected=True

            if head_detected or no_vest_detected:
                annotated_frames=[helmet_result.plot(),vest_result.plot()]
                return True, annotated_frames
            else:
                return False, []
        elif alarm_case_code==1:
            # logger.info("本次帧分析的目标告警场景：区域入侵（是否存在人体、车辆）")
            person_vehicle_result=cls.person_vehicle_model(frame, classes=[0,1,2,3,4,5,6,7], imgsz=640)[0]
            person_detected=len(person_vehicle_result.boxes)>0
            annotated_frames=[person_vehicle_result.plot()]
            return person_detected, annotated_frames
        elif alarm_case_code==2:
            # logger.info("本次帧分析的目标告警场景：火警（是否存在火焰、烟雾）")
            fire_smoke_result=cls.fire_smoke_model(frame, imgsz=640)[0]
            fire_or_smoke_detected=len(fire_smoke_result.boxes)>0
            annotated_frames=[fire_smoke_result.plot()]
            return fire_or_smoke_detected, annotated_frames
        else:
            logger.info("本次帧分析失败: 目标告警场景未知")
            return None, []


