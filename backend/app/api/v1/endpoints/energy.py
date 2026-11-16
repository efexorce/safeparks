from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from app.db.session import get_db
from app.services.energy_service import EnergyService
from app.schemas.energy import (
    EnergyReadingCreate, EnergyReadingResponse, SolarPanelResponse
)

router = APIRouter()


@router.post("/readings", response_model=EnergyReadingResponse)
async def record_energy_reading(
    data: EnergyReadingCreate,
    db: AsyncSession = Depends(get_db),
):
    service = EnergyService(db)
    return await service.record_reading(data)


@router.get("/city-stats", response_model=dict)
async def get_city_energy_stats(db: AsyncSession = Depends(get_db)):
    service = EnergyService(db)
    return await service.get_city_energy_stats()


@router.get("/solar-panels", response_model=List[SolarPanelResponse])
async def get_solar_panels(db: AsyncSession = Depends(get_db)):
    service = EnergyService(db)
    return await service.get_solar_panels()


@router.get("/cameras/{camera_id}/history", response_model=List[EnergyReadingResponse])
async def get_camera_energy_history(
    camera_id: UUID,
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    if not from_date:
        from_date = datetime.utcnow() - timedelta(hours=24)
    if not to_date:
        to_date = datetime.utcnow()
    service = EnergyService(db)
    return await service.get_camera_energy_history(camera_id, from_date, to_date)
