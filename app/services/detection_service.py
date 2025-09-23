from torch.mtia import snapshot
from ultralytics import YOLO
from pathlib import Path
from app.objects.alarm_case import AlarmCase
from app.utils.logger import get_logger

logger = get_logger(__name__)
# 模型推理服务
class DetectionService:
    descs = ["安全规范(未戴安全帽、未穿反光衣)", "区域入侵(人)", "火警(火焰、烟雾)"]
    # 告警类型描述+编码，对应AlarmDB中alarm_type字段
    desc_and_code = {"安全规范": 0, "区域入侵": 1, "火警": 2}

    # 加载YOLOv11预训练模型（安全帽检测）
    model=YOLO('yolo11n.pt')

    helmet_model=YOLO('yolo11n.pt') # 安全帽检测模型
    vest_model=YOLO('yolo11n.pt') # 反光衣检测模型
    ppe_model=YOLO('yolo11n.pt') # 个人防具检测模型

    person_model=YOLO('yolo11n.pt') # 人体检测模型
    fire_smoke_model=YOLO('yolo11n.pt') # 火焰烟雾检测模型

    # # 使用Path获取项目根目录
    # project_root = Path(__file__).parent.parent.parent
    # # 构建模型文件路径
    # model_path = project_root / 'small_best.pt'
    # model = YOLO(model_path)  # 加载本地模型, 假设该模型能够完成目标类别对象的检测。

    # 人在COCO数据集中的的类别ID是0
    person_class_id = 0
    # 安全帽，类别ID为-1表示当前模型还无法失败
    helmet_class_id = -1
    # 反光背心
    reflective_vest_class_id = -2
    # 火焰
    fire_class_id = -3
    # 烟雾
    smoke_class_id = -4

    # 置信度阈值
    confidence_threshold = 0.5

    @classmethod
    def detect_alarm_case(cls,frame, alarm_case_code):
        if alarm_case_code==0:
            logger.info("目标告警场景：安全规范（是否佩戴安全帽、是否穿戴反光衣）")

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

            annotated_frames=[helmet_result.plot(),vest_result.plot()]
            return head_detected or no_vest_detected, annotated_frames
        elif alarm_case_code==1:
            logger.info("目标告警场景：区域入侵（是否存在人体）")
            person_result=cls.person_model(frame,imgsz=640)[0]
            person_detected=len(person_result.boxes)>0
            annotated_frames=[person_result.plot()]
            return person_detected, annotated_frames
        elif alarm_case_code==2:
            logger.info("目标告警场景：火警（是否存在火焰、烟雾）")
            fire_smoke_result=cls.fire_smoke_model(frame,imgsz=640)[0]
            fire_or_smoke_detected=len(fire_smoke_result.boxes)>0
            annotated_frames=[fire_smoke_result.plot()]
            return fire_or_smoke_detected, annotated_frames
        else:
            logger.info("目标告警场景：未知")
            return None, []


