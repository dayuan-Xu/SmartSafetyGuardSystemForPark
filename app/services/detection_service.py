from ultralytics import YOLO
from pathlib import Path
from app.objects.alarm_case import AlarmCase


# 模型推理服务
class DetectionService:
    # 加载YOLOv11预训练模型（安全帽检测）
    # 使用Path获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    # 构建模型文件路径
    model_path = project_root / 'nano_best.pt'
    model = YOLO(model_path)  # 加载本地模型

    # 人在数据集中的的类别ID是0
    person_class_id = 0
    # 安全帽，类别ID为-1表示当前模型还无法失败
    helmet_class_id = -1
    # 反光背心
    reflective_vest_class_id = -1
    # 火焰
    fire_class_id = -1
    # 烟雾
    smoke_class_id = -1

    # 置信度阈值
    confidence_threshold = 0.5

    def detect_alarm_0(self, frame):
        """检测图像中的安全规范：未戴安全帽 or 未穿反光衣"""
        if frame is None:
            return None, None

        # 模型推理
        results = self.model(frame, conf=self.confidence_threshold)

        # 分析结果
        safety_alarm_case = None  # 该帧中检测出来的告警场景
        person_num = 0
        helmet_num = 0
        reflective_vest_num = 0
        for result in results:
            for box in result.boxes:  # 遍历每个框（每个对象）
                class_id = int(box.cls[0])
                # 是人
                if class_id == self.person_class_id:
                    person_num += 1
                # 是戴在人头上的安全帽
                elif class_id == self.helmet_class_id:
                    helmet_num += 1
                elif class_id == self.reflective_vest_class_id:
                    reflective_vest_num += 1

            if person_num > 0 and (helmet_num < person_num or reflective_vest_num < person_num):
                safety_alarm_case = AlarmCase(code=AlarmCase.desc_and_code["安全规范"])
        # 返回结果：AlarmCase对象，标注的图片（标准的OpenCV图像格式：BGR通道的HWC格式，和入参frame的格式一样）
        return safety_alarm_case, results[0].plot() if results else frame

    def detect_alarm_1(self, frame):
        """检测图像中的区域入侵"""
        if frame is None:
            return None, None

        # 模型推理
        results = self.model(frame, conf=self.confidence_threshold)

        # 分析结果
        intrude_alarm_case = None  # 该帧中检测出来的告警场景
        person_num = 0
        for result in results:
            for box in result.boxes:  # 遍历每个框（每个对象）
                class_id = int(box.cls[0])
                # 是人
                if class_id == self.person_class_id:
                    person_num += 1
            if person_num > 0:
                intrude_alarm_case = AlarmCase(code=AlarmCase.desc_and_code["区域入侵"])

        # 返回结果：AlarmCase列表，标注的图片（标准的OpenCV图像格式：BGR通道的HWC格式，和入参frame的格式一样）
        return intrude_alarm_case, results[0].plot() if results else frame

    def detect_alarm_2(self, frame):
        """检测图像中的火警"""
        if frame is None:
            return None, None

        # 模型推理
        results = self.model(frame, conf=self.confidence_threshold)

        # 分析结果
        fire_alarm_case = None  # 该帧中检测出来的告警场景
        fire_presence = False
        smoke_presence = False
        for result in results:
            for box in result.boxes:  # 遍历每个框（每个对象）
                class_id = int(box.cls[0])
                if class_id == self.fire_class_id:
                    fire_presence = True
                elif class_id == self.smoke_class_id:
                    smoke_presence = True

            if fire_presence and smoke_presence:
                fire_alarm_case = AlarmCase(code=AlarmCase.desc_and_code["火警"])

        # 返回结果：AlarmCase对象，标注的图片（标准的OpenCV图像格式：BGR通道的HWC格式，和入参frame的格式一样）
        return fire_alarm_case, results[0].plot() if results else frame

    def detect_alarm_012(self, frame):
        """同时检测图像中是否存在3种告警场景"""
        if frame is None:
            return None, None

        # 模型推理
        results = self.model(frame, conf=self.confidence_threshold)

        # 分析结果
        alarm_cases=[]  # 该帧中检测出来的告警场景列表
        person_num=0
        helmet_num=0
        reflective_vest_num=0
        fire_presence=False
        smoke_presence=False
        for result in results:
            for box in result.boxes: # 遍历每个框（每个对象）
                class_id = int(box.cls[0])
                # 是人
                if class_id == self.person_class_id:
                    person_num += 1
                # 是戴在人头上的安全帽
                elif class_id == self.helmet_class_id:
                    helmet_num += 1
                elif class_id == self.reflective_vest_class_id:
                    reflective_vest_num += 1
                elif class_id == self.fire_class_id:
                    fire_presence = True
                elif class_id == self.smoke_class_id:
                    smoke_presence = True

        # 构造要返回的告警场景列表
        if fire_presence and smoke_presence:
            fire_alarm_case=AlarmCase(code=AlarmCase.desc_and_code["火警"])
            alarm_cases.append(fire_alarm_case)
        if person_num > 0:
            intrude_alarm_case=AlarmCase(code=AlarmCase.desc_and_code["区域入侵"])
            alarm_cases.append(intrude_alarm_case)
        if person_num > 0 and (helmet_num < person_num or reflective_vest_num < person_num):
            safety_alarm_case=AlarmCase(code=AlarmCase.desc_and_code["安全规范"])
            alarm_cases.append(safety_alarm_case)

        # 返回结果：AlarmCase列表，标注的图片（标准的OpenCV图像格式：BGR通道的HWC格式，和入参frame的格式一样）
        return alarm_cases, results[0].plot() if results else frame


    def detect(self, frame, analysis_mode):
        if analysis_mode == 2:
            return self.detect_alarm_0(frame)
        elif analysis_mode == 3:
            return self.detect_alarm_1(frame)
        elif analysis_mode == 4:
            return self.detect_alarm_2(frame)
        return None