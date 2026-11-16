from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.alarm import AlarmType, AlarmSeverity, AlarmStatus


class AlarmCreate(BaseModel):
    camera_id: UUID
    event_id: Optional[UUID] = None
    alarm_type: AlarmType
    severity: AlarmSeverity = AlarmSeverity.MEDIUM
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    description: Optional[str] = None
    thumbnail_path: Optional[str] = None
    clip_path: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    detection_latency_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class AlarmUpdate(BaseModel):
    status: Optional[AlarmStatus] = None
    description: Optional[str] = None
    false_positive_reason: Optional[str] = None
    severity: Optional[AlarmSeverity] = None


class AlarmResponse(BaseModel):
    id: UUID
    camera_id: UUID
    event_id: Optional[UUID]
    alarm_type: AlarmType
    severity: AlarmSeverity
    status: AlarmStatus
    confidence_score: Optional[float]
    description: Optional[str]
    thumbnail_path: Optional[str]
    clip_path: Optional[str]
    triggered_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    notification_sent: bool
    location_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    detection_latency_ms: Optional[float]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class AlarmListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    alarms: List[AlarmResponse]


class AlarmSummaryResponse(BaseModel):
    total: int
    pending: int
    acknowledged: int
    resolved: int
    false_positives: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
    average_resolution_time_minutes: Optional[float]
