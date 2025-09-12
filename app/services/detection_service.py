from ultralytics import YOLO
import cv2
import numpy as np
import time


class DetectionService:
    def __init__(self):
        # 加载YOLOv8预训练模型（安全帽检测）
        self.model = YOLO('yolov8n.pt')  # 使用nano版本，速度快
        # 安全帽在COCO数据集中的类别ID是39(头盔)
        self.helmet_class_id = 39
        self.confidence_threshold = 0.5  # 置信度阈值

    def detect_helmet(self, frame):
        """检测图像中是否有人未戴安全帽"""
        if frame is None:
            return False, []

        # 转换为RGB格式（YOLO模型要求）
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 模型推理
        results = self.model(rgb_frame, conf=self.confidence_threshold)

        # 分析结果：检测到的人(0类)且未检测到安全帽，视为违规
        has_person = False
        has_helmet = False

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                # 检测到人
                if class_id == 0:  # COCO数据集中"人"的类别ID是0
                    has_person = True
                # 检测到安全帽
                elif class_id == self.helmet_class_id:
                    has_helmet = True

        # 判定规则：有人但没有检测到安全帽 → 违规
        is_violation = has_person and not has_helmet
        return is_violation, results[0].plot() if results else frame