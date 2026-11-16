import time
import logging
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logger.warning("ONNX Runtime not available, using mock inference")

try:
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True
except ImportError:
    try:
        import tensorflow as tf
        tflite = tf.lite
        TFLITE_AVAILABLE = True
    except ImportError:
        TFLITE_AVAILABLE = False


class EventType(str, Enum):
    VANDALISM = "vandalism"
    FIGHT = "fight"
    PERSON_DOWN = "person_down"
    SUSPICIOUS_OBJECT = "suspicious_object"
    MOTION = "motion"
    NO_EVENT = "no_event"


@dataclass
class DetectionResult:
    event_type: EventType
    confidence: float
    bounding_box: Optional[Dict[str, float]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    frame_id: Optional[int] = None
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return self.confidence >= 0.65 and self.event_type != EventType.NO_EVENT


@dataclass
class TemporalBuffer:
    max_size: int = 5
    events: List[DetectionResult] = field(default_factory=list)

    def add(self, result: DetectionResult) -> None:
        self.events.append(result)
        if len(self.events) > self.max_size:
            self.events.pop(0)

    def get_confirmed_event(self) -> Optional[DetectionResult]:
        if len(self.events) < 2:
            return None
        type_counts: Dict[EventType, List[float]] = {}
        for e in self.events:
            if e.event_type != EventType.NO_EVENT:
                if e.event_type not in type_counts:
                    type_counts[e.event_type] = []
                type_counts[e.event_type].append(e.confidence)
        for event_type, confidences in type_counts.items():
            if len(confidences) >= 2:
                avg_confidence = sum(confidences) / len(confidences)
                if avg_confidence >= 0.65:
                    best = max(
                        (e for e in self.events if e.event_type == event_type),
                        key=lambda x: x.confidence
                    )
                    return best
        return None


class ImageEnhancer:
    @staticmethod
    def enhance(frame: np.ndarray) -> np.ndarray:
        enhanced = ImageEnhancer._denoise(frame)
        enhanced = ImageEnhancer._normalize_brightness(enhanced)
        return enhanced

    @staticmethod
    def _denoise(frame: np.ndarray) -> np.ndarray:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        if len(frame.shape) == 3:
            result = np.zeros_like(frame, dtype=np.float32)
            for c in range(frame.shape[2]):
                from scipy.ndimage import convolve
                result[:, :, c] = convolve(frame[:, :, c].astype(np.float32), kernel)
            return np.clip(result, 0, 255).astype(np.uint8)
        return frame

    @staticmethod
    def _normalize_brightness(frame: np.ndarray) -> np.ndarray:
        mean_brightness = frame.mean()
        if mean_brightness < 50:
            factor = min(2.0, 128.0 / max(mean_brightness, 1))
            return np.clip(frame.astype(np.float32) * factor, 0, 255).astype(np.uint8)
        return frame


class EventDetector:
    INPUT_SIZE = (416, 416)
    CONFIDENCE_THRESHOLD = 0.65
    NMS_THRESHOLD = 0.45

    def __init__(self, model_path: Optional[str] = None, use_onnx: bool = True):
        self.model_path = model_path
        self.use_onnx = use_onnx and ONNX_AVAILABLE
        self.session = None
        self.interpreter = None
        self.temporal_buffer = TemporalBuffer(max_size=5)
        self.enhancer = ImageEnhancer()
        self._frame_count = 0
        self._is_loaded = False

        if model_path:
            self._load_model(model_path)

    def _load_model(self, model_path: str) -> None:
        try:
            if self.use_onnx and model_path.endswith(".onnx"):
                providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
                sess_options = ort.SessionOptions()
                sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                self.session = ort.InferenceSession(model_path, sess_options=sess_options, providers=providers)
                self._is_loaded = True
                logger.info(f"ONNX model loaded: {model_path}")
            elif TFLITE_AVAILABLE and model_path.endswith(".tflite"):
                self.interpreter = tflite.Interpreter(model_path=model_path)
                self.interpreter.allocate_tensors()
                self._is_loaded = True
                logger.info(f"TFLite model loaded: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model {model_path}: {e}")
            self._is_loaded = False

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        enhanced = self.enhancer.enhance(frame)
        resized = self._resize(enhanced, self.INPUT_SIZE)
        normalized = resized.astype(np.float32) / 255.0
        return np.expand_dims(normalized, axis=0)

    def _resize(self, frame: np.ndarray, target: Tuple[int, int]) -> np.ndarray:
        h, w = frame.shape[:2]
        target_w, target_h = target
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        small = frame[:new_h, :new_w] if len(frame.shape) == 3 else frame
        resized[:new_h, :new_w] = small
        return resized

    def infer(self, preprocessed: np.ndarray) -> List[DetectionResult]:
        start = time.perf_counter()
        if not self._is_loaded:
            return self._mock_inference(preprocessed)
        try:
            if self.session:
                input_name = self.session.get_inputs()[0].name
                outputs = self.session.run(None, {input_name: preprocessed})
                return self._parse_onnx_output(outputs, time.perf_counter() - start)
            elif self.interpreter:
                input_details = self.interpreter.get_input_details()
                self.interpreter.set_tensor(input_details[0]["index"], preprocessed)
                self.interpreter.invoke()
                output_details = self.interpreter.get_output_details()
                outputs = [self.interpreter.get_tensor(o["index"]) for o in output_details]
                return self._parse_tflite_output(outputs, time.perf_counter() - start)
        except Exception as e:
            logger.error(f"Inference error: {e}")
        return []

    def _parse_onnx_output(self, outputs: list, elapsed: float) -> List[DetectionResult]:
        results = []
        if not outputs or len(outputs) == 0:
            return results
        boxes = outputs[0] if len(outputs) > 0 else np.array([])
        scores = outputs[1] if len(outputs) > 1 else np.array([])
        classes = outputs[2] if len(outputs) > 2 else np.array([])

        class_map = {0: EventType.VANDALISM, 1: EventType.FIGHT, 2: EventType.PERSON_DOWN, 3: EventType.SUSPICIOUS_OBJECT}
        for i in range(min(len(scores[0]) if scores.ndim > 1 else len(scores), 10)):
            score = float(scores[0][i] if scores.ndim > 1 else scores[i])
            if score >= self.CONFIDENCE_THRESHOLD:
                cls_id = int(classes[0][i] if classes.ndim > 1 else classes[i])
                event_type = class_map.get(cls_id, EventType.MOTION)
                box = boxes[0][i].tolist() if boxes.ndim > 2 else boxes[i].tolist()
                results.append(DetectionResult(
                    event_type=event_type,
                    confidence=score,
                    bounding_box={"x": box[0], "y": box[1], "w": box[2], "h": box[3]} if len(box) >= 4 else None,
                    processing_time_ms=elapsed * 1000,
                ))
        return results

    def _parse_tflite_output(self, outputs: list, elapsed: float) -> List[DetectionResult]:
        return self._parse_onnx_output(outputs, elapsed)

    def _mock_inference(self, frame: np.ndarray) -> List[DetectionResult]:
        self._frame_count += 1
        if self._frame_count % 50 == 0:
            import random
            event_types = [EventType.VANDALISM, EventType.MOTION, EventType.NO_EVENT]
            weights = [0.05, 0.15, 0.80]
            chosen = random.choices(event_types, weights=weights)[0]
            confidence = random.uniform(0.70, 0.95) if chosen != EventType.NO_EVENT else 0.0
            return [DetectionResult(event_type=chosen, confidence=confidence, processing_time_ms=8.5)]
        return [DetectionResult(event_type=EventType.NO_EVENT, confidence=0.0)]

    def detect(self, frame: np.ndarray) -> Optional[DetectionResult]:
        preprocessed = self.preprocess(frame)
        raw_results = self.infer(preprocessed)
        best = None
        for r in raw_results:
            if r.event_type != EventType.NO_EVENT and r.confidence >= self.CONFIDENCE_THRESHOLD:
                if best is None or r.confidence > best.confidence:
                    best = r
        if best is None:
            best = DetectionResult(event_type=EventType.NO_EVENT, confidence=0.0)
        self.temporal_buffer.add(best)
        confirmed = self.temporal_buffer.get_confirmed_event()
        return confirmed
