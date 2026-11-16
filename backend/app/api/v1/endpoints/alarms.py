from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.services.alarm_service import AlarmService
from app.services.notification_service import notification_service
from app.schemas.alarm import (
    AlarmCreate, AlarmUpdate, AlarmResponse,
    AlarmListResponse, AlarmSummaryResponse
)
from app.models.alarm import AlarmType, AlarmSeverity, AlarmStatus

router = APIRouter()


@router.get("/", response_model=AlarmListResponse)
async def list_alarms(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: Optional[AlarmStatus] = None,
    alarm_type: Optional[AlarmType] = None,
    severity: Optional[AlarmSeverity] = None,
    camera_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
):
    service = AlarmService(db)
    alarms, total = await service.get_alarms(
        page, page_size, status, alarm_type, severity, camera_id, from_date, to_date
    )
    return AlarmListResponse(total=total, page=page, page_size=page_size, alarms=alarms)


@router.post("/", response_model=AlarmResponse, status_code=status.HTTP_201_CREATED)
async def create_alarm(
    data: AlarmCreate,
    db: AsyncSession = Depends(get_db),
):
    service = AlarmService(db)
    alarm = await service.create_alarm(data)
    if not alarm:
        raise HTTPException(status_code=422, detail="Alarm suppressed (low confidence or duplicate)")
    return alarm


@router.get("/summary", response_model=dict)
async def get_alarm_summary(db: AsyncSession = Depends(get_db)):
    service = AlarmService(db)
    return await service.get_summary()


@router.get("/{alarm_id}", response_model=AlarmResponse)
async def get_alarm(
    alarm_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = AlarmService(db)
    alarm = await service.get_alarm(alarm_id)
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    return alarm


@router.post("/{alarm_id}/acknowledge", response_model=AlarmResponse)
async def acknowledge_alarm(
    alarm_id: UUID,
    user_id: UUID = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
):
    service = AlarmService(db)
    alarm = await service.acknowledge_alarm(alarm_id, user_id)
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    return alarm


@router.post("/{alarm_id}/resolve", response_model=AlarmResponse)
async def resolve_alarm(
    alarm_id: UUID,
    user_id: UUID = Body(..., embed=True),
    notes: Optional[str] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
):
    service = AlarmService(db)
    alarm = await service.resolve_alarm(alarm_id, user_id, notes)
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    return alarm


@router.post("/{alarm_id}/false-positive", response_model=AlarmResponse)
async def mark_false_positive(
    alarm_id: UUID,
    user_id: UUID = Body(..., embed=True),
    reason: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
):
    service = AlarmService(db)
    alarm = await service.mark_false_positive(alarm_id, user_id, reason)
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    return alarm
