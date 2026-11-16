import logging
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.energy import EnergyReading, SolarPanel, PowerSource
from app.models.camera import Camera
from app.schemas.energy import EnergyReadingCreate
from app.core.config import settings

logger = logging.getLogger(__name__)

CAMERA_POWER_ACTIVE_W = 15.0
CAMERA_POWER_SLEEP_W = 5.0
ELECTRICITY_COST_PER_KWH = 0.12


class EnergyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_reading(self, data: EnergyReadingCreate) -> EnergyReading:
        reading = EnergyReading(**data.model_dump())
        self.db.add(reading)
        await self.db.flush()
        await self.db.refresh(reading)
        return reading

    async def get_city_energy_stats(self) -> dict:
        latest_subq = (
            select(
                EnergyReading.camera_id,
                func.max(EnergyReading.recorded_at).label("latest")
            )
            .group_by(EnergyReading.camera_id)
            .subquery()
        )
        result = await self.db.execute(
            select(
                func.sum(EnergyReading.power_consumption_w).label("total_consumption_w"),
                func.sum(EnergyReading.solar_output_w).label("total_solar_w"),
                func.count(EnergyReading.camera_id).label("total_cameras"),
                func.sum(
                    func.cast(EnergyReading.is_sleep_mode == True, Integer)
                ).label("sleep_cameras"),
            ).join(
                latest_subq,
                and_(
                    EnergyReading.camera_id == latest_subq.c.camera_id,
                    EnergyReading.recorded_at == latest_subq.c.latest,
                )
            )
        )
        row = result.one()
        total_w = float(row.total_consumption_w or 0)
        solar_w = float(row.total_solar_w or 0)
        sleep_cameras = int(row.sleep_cameras or 0)
        total_cameras = int(row.total_cameras or 0)
        saved_w = sleep_cameras * (CAMERA_POWER_ACTIVE_W - CAMERA_POWER_SLEEP_W)
        solar_ratio = (solar_w / total_w * 100) if total_w > 0 else 0

        return {
            "total_consumption_kw": round(total_w / 1000, 3),
            "total_solar_output_kw": round(solar_w / 1000, 3),
            "solar_ratio_percent": round(solar_ratio, 2),
            "cameras_in_sleep": sleep_cameras,
            "total_cameras": total_cameras,
            "energy_saved_kwh": round(saved_w / 1000, 3),
            "cost_saved_usd": round((saved_w / 1000) * ELECTRICITY_COST_PER_KWH, 4),
        }

    async def get_solar_panels(self) -> List[SolarPanel]:
        result = await self.db.execute(select(SolarPanel).where(SolarPanel.is_active == True))
        return list(result.scalars().all())

    async def get_camera_energy_history(
        self,
        camera_id: UUID,
        from_date: datetime,
        to_date: datetime,
    ) -> List[EnergyReading]:
        result = await self.db.execute(
            select(EnergyReading).where(
                and_(
                    EnergyReading.camera_id == camera_id,
                    EnergyReading.recorded_at >= from_date,
                    EnergyReading.recorded_at <= to_date,
                )
            ).order_by(EnergyReading.recorded_at)
        )
        return list(result.scalars().all())


from sqlalchemy import Integer
