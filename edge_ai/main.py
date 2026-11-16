import asyncio
import logging
import os
import httpx
from typing import Dict, Optional

from edge_ai.processors.stream_processor import StreamProcessor, ProcessorConfig
from edge_ai.processors.event_detector import DetectionResult
from edge_ai.models.model_manager import ModelManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
CAMERA_ID = os.getenv("CAMERA_ID", "")
RTSP_URL = os.getenv("RTSP_URL", "")
MODEL_PATH = os.getenv("MODEL_PATH", "")
AI_FPS = int(os.getenv("AI_FPS", "5"))


async def on_motion_change(camera_id: str, motion_detected: bool) -> None:
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{BACKEND_URL}/api/v1/cameras/{camera_id}/motion",
                params={"motion_detected": motion_detected},
                timeout=5.0,
            )
            logger.info(f"Motion status sent: camera={camera_id} motion={motion_detected}")
        except Exception as e:
            logger.error(f"Failed to send motion status: {e}")


async def on_event_detected(camera_id: str, event: DetectionResult) -> None:
    payload = {
        "camera_id": camera_id,
        "alarm_type": event.event_type.value,
        "confidence_score": event.confidence,
        "bounding_box": event.bounding_box,
        "detection_latency_ms": event.processing_time_ms,
        "metadata": {"frame_id": event.frame_id},
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{BACKEND_URL}/api/v1/alarms/",
                json=payload,
                timeout=5.0,
            )
            if resp.status_code == 201:
                logger.warning(f"Alarm created: {event.event_type} camera={camera_id}")
            else:
                logger.error(f"Failed to create alarm: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Failed to send event to backend: {e}")


async def main() -> None:
    if not CAMERA_ID:
        raise ValueError("CAMERA_ID environment variable is required")

    model_manager = ModelManager(models_dir="./edge_ai/models")
    model_path = MODEL_PATH or model_manager.get_model_path("unified_detector")

    config = ProcessorConfig(
        camera_id=CAMERA_ID,
        rtsp_url=RTSP_URL or None,
        ai_fps=AI_FPS,
        model_path=model_path,
        on_motion_change=on_motion_change,
        on_event_detected=on_event_detected,
    )

    processor = StreamProcessor(config)
    logger.info(f"Edge AI starting: camera={CAMERA_ID} model={model_path}")
    await processor.start()


if __name__ == "__main__":
    asyncio.run(main())
