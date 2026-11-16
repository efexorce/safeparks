import numpy as np
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def decode_frame(data: bytes) -> Optional[np.ndarray]:
    if CV2_AVAILABLE:
        arr = np.frombuffer(data, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    logger.warning("cv2 not available for frame decoding")
    return None


def encode_frame(frame: np.ndarray, quality: int = 85) -> Optional[bytes]:
    if CV2_AVAILABLE:
        _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        return buf.tobytes()
    return None


def resize_frame(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    if CV2_AVAILABLE:
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    current_h, current_w = frame.shape[:2]
    scale_h = height / current_h
    scale_w = width / current_w
    scale = min(scale_h, scale_w)
    new_h = int(current_h * scale)
    new_w = int(current_w * scale)
    indices_h = (np.arange(new_h) / scale).astype(int)
    indices_w = (np.arange(new_w) / scale).astype(int)
    return frame[np.ix_(indices_h, indices_w)]


def apply_fog_removal(frame: np.ndarray) -> np.ndarray:
    if not CV2_AVAILABLE:
        return frame
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_channel = clahe.apply(l_channel)
    enhanced = cv2.merge([l_channel, a, b])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


def apply_night_enhancement(frame: np.ndarray) -> np.ndarray:
    if not CV2_AVAILABLE:
        return np.clip(frame.astype(np.float32) * 2.0, 0, 255).astype(np.uint8)
    gamma = 0.5
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(frame, table)


def apply_rain_removal(frame: np.ndarray) -> np.ndarray:
    if not CV2_AVAILABLE:
        return frame
    return cv2.bilateralFilter(frame, d=9, sigmaColor=75, sigmaSpace=75)


def auto_enhance(frame: np.ndarray, conditions: Optional[str] = None) -> np.ndarray:
    if conditions == "fog":
        return apply_fog_removal(frame)
    if conditions == "night":
        return apply_night_enhancement(frame)
    if conditions == "rain":
        return apply_rain_removal(frame)
    mean_brightness = frame.mean()
    if mean_brightness < 40:
        return apply_night_enhancement(frame)
    return frame
