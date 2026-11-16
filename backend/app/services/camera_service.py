import logging
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, and_, or_
from sqlalchemy.orm import selectinload

from app.models.camera import Camera, CameraEvent, BandwidthUsage, CameraStatus, CameraQualityMode, AIStatus
from app.schemas.camera import CameraCreate, CameraUpdate
from app.core.config import settings

logger = logging.getLogger(__name__)


class CameraService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_camera(self, data: CameraCreate) -> Camera:
        camera = Camera(**data.model_dump())
        self.db.add(camera)
        await self.db.flush()
        await self.db.refresh(camera)
        logger.info(f"Camera created: {camera.id} - {camera.name}")
        return camera

    async def get_camera(self, camera_id: UUID) -> Optional[Camera]:
        result = await self.db.execute(
            select(Camera).where(Camera.id == camera_id)
        )
        return result.scalar_one_or_none()

    async def get_cameras(
        self,
        page: int = 1,
        page_size: int = 50,
        status: Optional[CameraStatus] = None,
        district: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Camera], int]:
        query = select(Camera)
        filters = []
        if status:
            filters.append(Camera.status == status)
        if district:
            filters.append(Camera.district == district)
        if is_active is not None:
            filters.append(Camera.is_active == is_active)
        if filters:
            query = query.where(and_(*filters))

        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        cameras = result.scalars().all()
        return list(cameras), total

    async def update_camera(self, camera_id: UUID, data: CameraUpdate) -> Optional[Camera]:
        camera = await self.get_camera(camera_id)
        if not camera:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(camera, key, value)
        camera.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(camera)
        return camera

    async def delete_camera(self, camera_id: UUID) -> bool:
        camera = await self.get_camera(camera_id)
        if not camera:
            return False
        camera.is_active = False
        camera.updated_at = datetime.utcnow()
        await self.db.flush()
        return True

    async def update_motion_status(self, camera_id: UUID, motion_detected: bool) -> Optional[Camera]:
        camera = await self.get_camera(camera_id)
        if not camera:
            return None
        camera.motion_detected = motion_detected
        if motion_detected:
            camera.last_motion_at = datetime.utcnow()
            camera.quality_mode = CameraQualityMode.HIGH
            camera.current_fps = settings.HIGH_QUALITY_FPS
            camera.current_bitrate_mbps = settings.HIGH_QUALITY_BITRATE_MBPS
            camera.current_resolution = settings.HIGH_QUALITY_RESOLUTION
            camera.ai_status = AIStatus.ACTIVE
        else:
            camera.quality_mode = CameraQualityMode.LOW
            camera.current_fps = settings.AI_ANALYSIS_FPS
            camera.current_bitrate_mbps = settings.LOW_QUALITY_BITRATE_MBPS
            camera.current_resolution = settings.LOW_QUALITY_RESOLUTION
            camera.ai_status = AIStatus.SLEEP
        camera.updated_at = datetime.utcnow()
        await self.db.flush()
        return camera

    async def check_bandwidth_quota(self, camera_id: UUID) -> dict:
        camera = await self.get_camera(camera_id)
        if not camera:
            return {}
        daily_remaining = settings.DAILY_DATA_LIMIT_GB - camera.daily_data_used_gb
        monthly_remaining = settings.MONTHLY_DATA_LIMIT_GB - camera.monthly_data_used_gb
        should_throttle = (
            daily_remaining < 1.0 or monthly_remaining < 10.0
        )
        if should_throttle and camera.quality_mode != CameraQualityMode.LOW:
            camera.quality_mode = CameraQualityMode.LOW
            camera.current_bitrate_mbps = settings.LOW_QUALITY_BITRATE_MBPS
            camera.current_resolution = settings.LOW_QUALITY_RESOLUTION
            camera.current_fps = settings.LOW_QUALITY_FPS
            await self.db.flush()
        return {
            "camera_id": str(camera_id),
            "daily_used_gb": camera.daily_data_used_gb,
            "daily_limit_gb": settings.DAILY_DATA_LIMIT_GB,
            "daily_remaining_gb": max(0, daily_remaining),
            "monthly_used_gb": camera.monthly_data_used_gb,
            "monthly_limit_gb": settings.MONTHLY_DATA_LIMIT_GB,
            "monthly_remaining_gb": max(0, monthly_remaining),
            "is_throttled": should_throttle,
        }

    async def get_map_data(self) -> List[dict]:
        result = await self.db.execute(
            select(
                Camera.id, Camera.name, Camera.latitude, Camera.longitude,
                Camera.status, Camera.ai_status, Camera.motion_detected,
                Camera.district, Camera.park_zone, Camera.daily_data_used_gb,
                Camera.current_resolution
            ).where(Camera.is_active == True)
        )
        rows = result.all()
        return [
            {
                "id": str(row.id),
                "name": row.name,
                "latitude": row.latitude,
                "longitude": row.longitude,
                "status": row.status,
                "ai_status": row.ai_status,
                "motion_detected": row.motion_detected,
                "district": row.district,
                "park_zone": row.park_zone,
                "daily_data_used_gb": row.daily_data_used_gb,
                "current_resolution": row.current_resolution,
            }
            for row in rows
        ]

    async def get_summary_stats(self) -> dict:
        result = await self.db.execute(
            select(
                func.count(Camera.id).label("total"),
                func.sum(func.cast(Camera.status == CameraStatus.ONLINE, Integer)).label("online"),
                func.sum(func.cast(Camera.status == CameraStatus.OFFLINE, Integer)).label("offline"),
                func.sum(func.cast(Camera.status == CameraStatus.SLEEP, Integer)).label("sleep"),
                func.sum(Camera.daily_data_used_gb).label("total_daily_gb"),
                func.sum(Camera.monthly_data_used_gb).label("total_monthly_gb"),
            ).where(Camera.is_active == True)
        )
        row = result.one()
        return {
            "total_cameras": row.total or 0,
            "online_cameras": row.online or 0,
            "offline_cameras": row.offline or 0,
            "sleep_cameras": row.sleep or 0,
            "total_daily_data_gb": float(row.total_daily_gb or 0),
            "total_monthly_data_gb": float(row.total_monthly_gb or 0),
        }


from sqlalchemy import Integer, cast
