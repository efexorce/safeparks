import asyncio
import logging
import time
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass

from edge_ai.processors.motion_detector import MotionDetector, MotionResult
from edge_ai.processors.event_detector import EventDetector, DetectionResult, EventType

logger = logging.getLogger(__name__)

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available")


@dataclass
class ProcessorConfig:
    camera_id: str
    rtsp_url: Optional[str] = None
    ai_fps: int = 5
    motion_threshold: float = 25.0
    model_path: Optional[str] = None
    use_onnx: bool = True
    on_motion_change: Optional[Callable[[str, bool], Awaitable[None]]] = None
    on_event_detected: Optional[Callable[[str, DetectionResult], Awaitable[None]]] = None


class StreamProcessor:
    def __init__(self, config: ProcessorConfig):
        self.config = config
        self.motion_detector = MotionDetector(threshold=config.motion_threshold)
        self.event_detector = EventDetector(model_path=config.model_path, use_onnx=config.use_onnx)
        self._running = False
        self._cap = None
        self._is_ai_active = False
        self._last_motion_time: Optional[float] = None
        self._sleep_timeout_seconds = 30
        self._frame_count = 0
        self._ai_frame_interval = 1

    async def start(self) -> None:
        self._running = True
        logger.info(f"StreamProcessor starting for camera {self.config.camera_id}")
        await self._process_loop()

    async def stop(self) -> None:
        self._running = False
        if self._cap and CV2_AVAILABLE:
            self._cap.release()
        logger.info(f"StreamProcessor stopped for camera {self.config.camera_id}")

    async def _process_loop(self) -> None:
        if CV2_AVAILABLE and self.config.rtsp_url:
            self._cap = cv2.VideoCapture(self.config.rtsp_url)
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        while self._running:
            frame = await self._capture_frame()
            if frame is None:
                await asyncio.sleep(1.0)
                continue

            self._frame_count += 1
            motion_result = self.motion_detector.detect(frame)
            await self._handle_motion(motion_result)

            if self._is_ai_active and self._frame_count % self._ai_frame_interval == 0:
                event = self.event_detector.detect(frame)
                if event and event.is_valid:
                    await self._handle_event(event)

            sleep_duration = self._calculate_sleep_duration()
            await asyncio.sleep(sleep_duration)

    async def _capture_frame(self):
        if CV2_AVAILABLE and self._cap and self._cap.isOpened():
            loop = asyncio.get_event_loop()
            ret, frame = await loop.run_in_executor(None, self._cap.read)
            if ret:
                return frame
        import numpy as np
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    async def _handle_motion(self, result: MotionResult) -> None:
        if result.motion_detected and not self._is_ai_active:
            self._is_ai_active = True
            self._last_motion_time = time.time()
            logger.info(f"Camera {self.config.camera_id}: Motion detected, activating AI")
            if self.config.on_motion_change:
                await self.config.on_motion_change(self.config.camera_id, True)
        elif not result.motion_detected and self._is_ai_active:
            idle_time = time.time() - (self._last_motion_time or time.time())
            if idle_time > self._sleep_timeout_seconds:
                self._is_ai_active = False
                logger.info(f"Camera {self.config.camera_id}: No motion, AI entering sleep")
                if self.config.on_motion_change:
                    await self.config.on_motion_change(self.config.camera_id, False)
        if result.motion_detected:
            self._last_motion_time = time.time()

    async def _handle_event(self, event: DetectionResult) -> None:
        logger.warning(
            f"Camera {self.config.camera_id}: Event detected: {event.event_type} "
            f"confidence={event.confidence:.2f} latency={event.processing_time_ms:.1f}ms"
        )
        if self.config.on_event_detected:
            await self.config.on_event_detected(self.config.camera_id, event)

    def _calculate_sleep_duration(self) -> float:
        if self._is_ai_active:
            return 1.0 / max(self.config.ai_fps, 1)
        return 0.5
