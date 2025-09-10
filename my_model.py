from ultralytics import YOLO
from ultralytics.data.utils import check_det_dataset

def predict(yolo_model,images_source):
    # Predict with the model
    results = yolo_model(images_source,show=True,stream=True,save=True)  # predict on an image

    # Access the results
    for result in results:
        xywh = result.boxes.xywh  # center-x, center-y, width, height
        xywhn = result.boxes.xywhn  # normalized
        xyxy = result.boxes.xyxy  # top-left-x, top-left-y, bottom-right-x, bottom-right-y
        xyxyn = result.boxes.xyxyn  # normalized
        names = [result.names[cls.item()] for cls in result.boxes.cls.int()]  # class name of each box
        confs = result.boxes.conf  # confidence score of each box
        # 以键值对格式打印上述变量
        print(f"xywh: {xywh}")
        print(f"xywhn: {xywhn}")
        print(f"xyxy: {xyxy}")
        print(f"xyxyn: {xyxyn}")
        print(f"names: {names}")
        print(f"confs: {confs}")

def train_model(yaml_file_path):
    # Load pretrained YOLO11n model
    model = YOLO("yolo11n.pt")
    # train model on custom dataset
    model.train(data=yaml_file_path, epochs=100, imgsz=640)
    return model


if __name__ == "__main__":
    # 只在直接运行此脚本时执行训练
    yaml_file_path=""
    trained_model = train_model(yaml_file_path)

