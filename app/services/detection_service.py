from ultralytics import YOLO
from pathlib import Path
from app.objects.alarm_case import AlarmCase


# 模型推理服务
class DetectionService:
    # 加载YOLOv11预训练模型（安全帽检测）
    model=YOLO('yolo11n.pt')

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