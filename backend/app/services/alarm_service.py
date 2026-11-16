import logging
from typing import List, Optional, Tuple, Dict
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, and_, case
from sqlalchemy.orm import selectinload

from app.models.alarm import Alarm, AlarmLog, AlarmType, AlarmSeverity, AlarmStatus
from app.schemas.alarm import AlarmCreate, AlarmUpdate

logger = logging.getLogger(__name__)

TEMPORAL_WINDOW_SECONDS = 5
MIN_CONFIDENCE_THRESHOLD = 0.65
SEVERITY_MAP = {
    AlarmType.FIGHT: AlarmSeverity.CRITICAL,
    AlarmType.PERSON_DOWN: AlarmSeverity.CRITICAL,
    AlarmType.FIRE: AlarmSeverity.CRITICAL,
    AlarmType.VANDALISM: AlarmSeverity.HIGH,
    AlarmType.SUSPICIOUS_OBJECT: AlarmSeverity.HIGH,
    AlarmType.INTRUSION: AlarmSeverity.MEDIUM,
    AlarmType.FLOOD: AlarmSeverity.HIGH,
    AlarmType.UNKNOWN: AlarmSeverity.LOW,
}


class AlarmService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_alarm(self, data: AlarmCreate) -> Optional[Alarm]:
        if data.confidence_score and data.confidence_score < MIN_CONFIDENCE_THRESHOLD:
            logger.info(f"Alarm suppressed: confidence {data.confidence_score} below threshold")
            return None

        duplicate = await self._check_duplicate_alarm(data)
        if duplicate:
            logger.info(f"Duplicate alarm suppressed for camera {data.camera_id}")
            return None

        if data.severity == AlarmSeverity.MEDIUM:
            data.severity = SEVERITY_MAP.get(data.alarm_type, AlarmSeverity.MEDIUM)

        alarm = Alarm(**data.model_dump())
        self.db.add(alarm)
        await self.db.flush()
        await self.db.refresh(alarm)

        log = AlarmLog(
            alarm_id=alarm.id,
            action="created",
            notes=f"Alarm auto-created by AI with confidence={data.confidence_score}",
        )
        self.db.add(log)
        await self.db.flush()

        logger.info(f"Alarm created: {alarm.id} type={alarm.alarm_type} severity={alarm.severity}")
        return alarm

    async def _check_duplicate_alarm(self, data: AlarmCreate) -> bool:
        window_start = datetime.utcnow() - timedelta(seconds=TEMPORAL_WINDOW_SECONDS * 6)
        result = await self.db.execute(
            select(func.count(Alarm.id)).where(
                and_(
                    Alarm.camera_id == data.camera_id,
                    Alarm.alarm_type == data.alarm_type,
                    Alarm.triggered_at >= window_start,
                    Alarm.status != AlarmStatus.FALSE_POSITIVE,
                )
            )
        )
        count = result.scalar_one()
        return count > 0

    async def acknowledge_alarm(self, alarm_id: UUID, user_id: UUID) -> Optional[Alarm]:
        alarm = await self.get_alarm(alarm_id)
        if not alarm:
            return None
        alarm.status = AlarmStatus.ACKNOWLEDGED
        alarm.acknowledged_at = datetime.utcnow()
        alarm.acknowledged_by = user_id
        await self.db.flush()

        log = AlarmLog(alarm_id=alarm_id, action="acknowledged", performed_by=user_id)
        self.db.add(log)
        await self.db.flush()
        return alarm

    async def resolve_alarm(self, alarm_id: UUID, user_id: UUID, notes: Optional[str] = None) -> Optional[Alarm]:
        alarm = await self.get_alarm(alarm_id)
        if not alarm:
            return None
        alarm.status = AlarmStatus.RESOLVED
        alarm.resolved_at = datetime.utcnow()
        alarm.resolved_by = user_id
        await self.db.flush()

        log = AlarmLog(alarm_id=alarm_id, action="resolved", performed_by=user_id, notes=notes)
        self.db.add(log)
        await self.db.flush()
        return alarm

    async def mark_false_positive(self, alarm_id: UUID, user_id: UUID, reason: str) -> Optional[Alarm]:
        alarm = await self.get_alarm(alarm_id)
        if not alarm:
            return None
        alarm.status = AlarmStatus.FALSE_POSITIVE
        alarm.false_positive_reason = reason
        alarm.resolved_at = datetime.utcnow()
        alarm.resolved_by = user_id
        if alarm.event_id:
            await self.db.execute(
                update(CameraEvent).where(CameraEvent.id == alarm.event_id).values(is_false_positive=True)
            )
        await self.db.flush()

        log = AlarmLog(alarm_id=alarm_id, action="marked_false_positive", performed_by=user_id, notes=reason)
        self.db.add(log)
        await self.db.flush()
        return alarm

    async def get_alarm(self, alarm_id: UUID) -> Optional[Alarm]:
        result = await self.db.execute(select(Alarm).where(Alarm.id == alarm_id))
        return result.scalar_one_or_none()

    async def get_alarms(
        self,
        page: int = 1,
        page_size: int = 50,
        status: Optional[AlarmStatus] = None,
        alarm_type: Optional[AlarmType] = None,
        severity: Optional[AlarmSeverity] = None,
        camera_id: Optional[UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Tuple[List[Alarm], int]:
        query = select(Alarm)
        filters = []
        if status:
            filters.append(Alarm.status == status)
        if alarm_type:
            filters.append(Alarm.alarm_type == alarm_type)
        if severity:
            filters.append(Alarm.severity == severity)
        if camera_id:
            filters.append(Alarm.camera_id == camera_id)
        if from_date:
            filters.append(Alarm.triggered_at >= from_date)
        if to_date:
            filters.append(Alarm.triggered_at <= to_date)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(Alarm.triggered_at.desc())

        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        alarms = result.scalars().all()
        return list(alarms), total

    async def get_summary(self) -> dict:
        result = await self.db.execute(
            select(
                func.count(Alarm.id).label("total"),
                func.sum(case((Alarm.status == AlarmStatus.PENDING, 1), else_=0)).label("pending"),
                func.sum(case((Alarm.status == AlarmStatus.ACKNOWLEDGED, 1), else_=0)).label("acknowledged"),
                func.sum(case((Alarm.status == AlarmStatus.RESOLVED, 1), else_=0)).label("resolved"),
                func.sum(case((Alarm.status == AlarmStatus.FALSE_POSITIVE, 1), else_=0)).label("false_positives"),
            )
        )
        row = result.one()
        return {
            "total": row.total or 0,
            "pending": row.pending or 0,
            "acknowledged": row.acknowledged or 0,
            "resolved": row.resolved or 0,
            "false_positives": row.false_positives or 0,
        }


from app.models.camera import CameraEvent
