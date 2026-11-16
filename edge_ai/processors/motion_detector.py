import logging
import time
import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MotionResult:
    motion_detected: bool
    motion_score: float
    motion_area_ratio: float
    processing_time_ms: float


class MotionDetector:
    def __init__(
        self,
        threshold: float = 25.0,
        min_area_ratio: float = 0.002,
        history_frames: int = 3,
    ):
        self.threshold = threshold
        self.min_area_ratio = min_area_ratio
        self.history_frames = history_frames
        self._prev_frames = []
        self._background = None

    def detect(self, frame: np.ndarray) -> MotionResult:
        start = time.perf_counter()
        gray = self._to_gray(frame)

        if self._background is None:
            self._background = gray.astype(np.float32)
            self._prev_frames.append(gray.copy())
            return MotionResult(False, 0.0, 0.0, 0.0)

        diff = np.abs(gray.astype(np.float32) - self._background)
        motion_pixels = np.sum(diff > self.threshold)
        total_pixels = gray.size
        area_ratio = motion_pixels / total_pixels
        motion_score = float(diff.mean())
        motion_detected = area_ratio >= self.min_area_ratio

        alpha = 0.05 if motion_detected else 0.2
        self._background = (1 - alpha) * self._background + alpha * gray.astype(np.float32)

        self._prev_frames.append(gray.copy())
        if len(self._prev_frames) > self.history_frames:
            self._prev_frames.pop(0)

        elapsed_ms = (time.perf_counter() - start) * 1000
        return MotionResult(
            motion_detected=motion_detected,
            motion_score=motion_score,
            motion_area_ratio=area_ratio,
            processing_time_ms=elapsed_ms,
        )

    def _to_gray(self, frame: np.ndarray) -> np.ndarray:
        if len(frame.shape) == 2:
            return frame
        weights = np.array([0.114, 0.587, 0.299], dtype=np.float32)
        return np.dot(frame[..., :3], weights).astype(np.uint8)

    def reset(self) -> None:
        self._prev_frames = []
        self._background = None
