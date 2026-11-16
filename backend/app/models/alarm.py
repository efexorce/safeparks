import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Boolean, DateTime,
    ForeignKey, Enum as SAEnum, Text, JSON, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.db.session import Base


class AlarmType(str, enum.Enum):
    VANDALISM = "vandalism"
    FIGHT = "fight"
    PERSON_DOWN = "person_down"
    SUSPICIOUS_OBJECT = "suspicious_object"
    INTRUSION = "intrusion"
    FIRE = "fire"
    FLOOD = "flood"
    UNKNOWN = "unknown"


class AlarmSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlarmStatus(str, enum.Enum):
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class Alarm(Base):
    __tablename__ = "alarms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False, index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("camera_events.id"), nullable=True)
    alarm_type = Column(SAEnum(AlarmType), nullable=False)
    severity = Column(SAEnum(AlarmSeverity), nullable=False, default=AlarmSeverity.MEDIUM)
    status = Column(SAEnum(AlarmStatus), default=AlarmStatus.PENDING, nullable=False)
    confidence_score = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    thumbnail_path = Column(String(500), nullable=True)
    clip_path = Column(String(500), nullable=True)
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    detection_latency_ms = Column(Float, nullable=True)
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime, nullable=True)
    false_positive_reason = Column(Text, nullable=True)
    location_name = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    camera = relationship("Camera", back_populates="alarms")
    event = relationship("CameraEvent", back_populates="alarm")
    logs = relationship("AlarmLog", back_populates="alarm", lazy="dynamic")


class AlarmLog(Base):
    __tablename__ = "alarm_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alarm_id = Column(UUID(as_uuid=True), ForeignKey("alarms.id"), nullable=False, index=True)
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    action = Column(String(100), nullable=False)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    alarm = relationship("Alarm", back_populates="logs")
