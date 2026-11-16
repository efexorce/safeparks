from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.alarm import Alarm, AlarmType, AlarmStatus
from app.models.camera import Camera, BandwidthUsage
from app.models.energy import EnergyReading

router = APIRouter()


@router.get("/daily")
async def daily_report(
    date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
):
    target_date = date or datetime.utcnow()
    day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    alarm_result = await db.execute(
        select(
            func.count(Alarm.id).label("total_alarms"),
            func.sum(func.cast(Alarm.status == AlarmStatus.RESOLVED, Integer)).label("resolved"),
            func.sum(func.cast(Alarm.status == AlarmStatus.FALSE_POSITIVE, Integer)).label("false_positives"),
        ).where(and_(Alarm.triggered_at >= day_start, Alarm.triggered_at < day_end))
    )
    alarm_row = alarm_result.one()

    bandwidth_result = await db.execute(
        select(
            func.sum(BandwidthUsage.bytes_sent + BandwidthUsage.bytes_received).label("total_bytes"),
        ).where(and_(BandwidthUsage.recorded_at >= day_start, BandwidthUsage.recorded_at < day_end))
    )
    bandwidth_row = bandwidth_result.one()

    energy_result = await db.execute(
        select(
            func.avg(EnergyReading.power_consumption_w).label("avg_power_w"),
            func.sum(EnergyReading.solar_output_w).label("total_solar_w"),
        ).where(and_(EnergyReading.recorded_at >= day_start, EnergyReading.recorded_at < day_end))
    )
    energy_row = energy_result.one()

    total_bytes = float(bandwidth_row.total_bytes or 0)

    return {
        "date": day_start.date().isoformat(),
        "alarms": {
            "total": alarm_row.total_alarms or 0,
            "resolved": alarm_row.resolved or 0,
            "false_positives": alarm_row.false_positives or 0,
        },
        "bandwidth": {
            "total_gb": round(total_bytes / (1024 ** 3), 3),
        },
        "energy": {
            "avg_consumption_w": round(float(energy_row.avg_power_w or 0), 2),
            "total_solar_output_w": round(float(energy_row.total_solar_w or 0), 2),
        },
    }


@router.get("/monthly")
async def monthly_report(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: AsyncSession = Depends(get_db),
):
    month_start = datetime(year, month, 1)
    if month == 12:
        month_end = datetime(year + 1, 1, 1)
    else:
        month_end = datetime(year, month + 1, 1)

    alarm_result = await db.execute(
        select(
            func.count(Alarm.id).label("total"),
            func.sum(func.cast(Alarm.status == AlarmStatus.FALSE_POSITIVE, Integer)).label("fp"),
        ).where(and_(Alarm.triggered_at >= month_start, Alarm.triggered_at < month_end))
    )
    alarm_row = alarm_result.one()

    camera_result = await db.execute(
        select(func.count(Camera.id)).where(Camera.is_active == True)
    )
    active_cameras = camera_result.scalar_one()

    return {
        "year": year,
        "month": month,
        "active_cameras": active_cameras,
        "alarms": {
            "total": alarm_row.total or 0,
            "false_positive_rate_percent": round(
                (alarm_row.fp or 0) / max(alarm_row.total or 1, 1) * 100, 2
            ),
        },
    }


from sqlalchemy import Integer
