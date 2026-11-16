import logging
from typing import Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

HIGH_BITRATE_MBPS = 3.0
LOW_BITRATE_MBPS = 0.8
HIGH_FPS = 25
LOW_FPS = 5
AI_FPS = 5
HIGH_RESOLUTION = "1080p"
LOW_RESOLUTION = "480p"
DAILY_LIMIT_GB = 13.5
MONTHLY_LIMIT_GB = 400.0
CODEC = "h265"


@dataclass
class StreamConfig:
    resolution: str
    fps: int
    bitrate_mbps: float
    codec: str
    reason: str


class BandwidthOptimizer:
    def __init__(self):
        self._camera_usage: Dict[str, Dict] = {}

    def get_optimal_config(
        self,
        camera_id: str,
        motion_detected: bool,
        daily_used_gb: float,
        monthly_used_gb: float,
    ) -> StreamConfig:
        daily_remaining = DAILY_LIMIT_GB - daily_used_gb
        monthly_remaining = MONTHLY_LIMIT_GB - monthly_used_gb

        if daily_remaining < 0.5 or monthly_remaining < 5.0:
            return StreamConfig(
                resolution=LOW_RESOLUTION,
                fps=LOW_FPS,
                bitrate_mbps=LOW_BITRATE_MBPS,
                codec=CODEC,
                reason="quota_exceeded",
            )

        if motion_detected:
            return StreamConfig(
                resolution=HIGH_RESOLUTION,
                fps=HIGH_FPS,
                bitrate_mbps=HIGH_BITRATE_MBPS,
                codec=CODEC,
                reason="motion_active",
            )

        return StreamConfig(
            resolution=LOW_RESOLUTION,
            fps=AI_FPS,
            bitrate_mbps=LOW_BITRATE_MBPS,
            codec=CODEC,
            reason="idle_mode",
        )

    def calculate_daily_usage(
        self, bitrate_mbps: float, active_hours: int = 24
    ) -> float:
        bits_per_second = bitrate_mbps * 1_000_000
        total_bits = bits_per_second * active_hours * 3600
        total_gb = total_bits / (8 * 1024**3)
        return round(total_gb, 2)

    def estimate_monthly_usage(self, daily_gb: float) -> float:
        return round(daily_gb * 30, 2)
