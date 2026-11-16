import logging
import os
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelManager:
    SUPPORTED_FORMATS = [".onnx", ".tflite"]

    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self._registry: Dict[str, dict] = {
            "vandalism_detector": {
                "filename": "vandalism_detector.onnx",
                "description": "Vandalism detection model (YOLOv8-nano)",
                "input_size": (416, 416),
                "classes": ["vandalism"],
            },
            "fight_detector": {
                "filename": "fight_detector.onnx",
                "description": "Fight/aggression detection model",
                "input_size": (416, 416),
                "classes": ["fight", "aggressive_behavior"],
            },
            "person_down_detector": {
                "filename": "person_down.onnx",
                "description": "Fallen/unconscious person detection",
                "input_size": (416, 416),
                "classes": ["person_down", "lying"],
            },
            "suspicious_object_detector": {
                "filename": "suspicious_object.onnx",
                "description": "Unattended/suspicious object detection",
                "input_size": (416, 416),
                "classes": ["abandoned_bag", "suspicious_package"],
            },
            "unified_detector": {
                "filename": "unified_safeparks.onnx",
                "description": "Unified multi-class detection model",
                "input_size": (416, 416),
                "classes": ["vandalism", "fight", "person_down", "suspicious_object"],
            },
        }

    def get_model_path(self, model_name: str) -> Optional[str]:
        if model_name not in self._registry:
            logger.error(f"Model not registered: {model_name}")
            return None
        meta = self._registry[model_name]
        path = self.models_dir / meta["filename"]
        if not path.exists():
            logger.warning(f"Model file not found: {path}. Using mock inference.")
            return None
        return str(path)

    def list_models(self) -> Dict[str, dict]:
        result = {}
        for name, meta in self._registry.items():
            path = self.models_dir / meta["filename"]
            result[name] = {**meta, "available": path.exists(), "path": str(path)}
        return result

    def register_model(self, name: str, filename: str, description: str, input_size: tuple, classes: list) -> None:
        self._registry[name] = {
            "filename": filename,
            "description": description,
            "input_size": input_size,
            "classes": classes,
        }
        logger.info(f"Model registered: {name}")

    def get_download_instructions(self) -> str:
        return """
Edge AI Model Download Instructions
====================================

1. SafeParks modelleri için Hailo Model Zoo veya ONNX Model Zoo kullanın.
   Genel amaçlı başlangıç modeli:

   # YOLOv8-nano ONNX (genel nesne tespiti için):
   pip install ultralytics
   yolo export model=yolov8n.pt format=onnx imgsz=416

2. Modeli fine-tune edin (transfer learning):
   from ultralytics import YOLO
   model = YOLO('yolov8n.pt')
   model.train(data='safeparks_dataset.yaml', epochs=100, imgsz=416)
   model.export(format='onnx')

3. Hailo-8 için:
   hailo optimize --hw-arch hailo8 --model unified_safeparks.onnx
   hailo compile --hw-arch hailo8 unified_safeparks_optimized.onnx

4. NVIDIA Jetson Nano için TensorRT:
   trtexec --onnx=unified_safeparks.onnx --saveEngine=unified_safeparks.trt

5. Modeli edge_ai/models/ dizinine kopyalayın.
"""
