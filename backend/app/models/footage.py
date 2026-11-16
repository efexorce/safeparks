import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


class FootageRecord(Base):
    __tablename__ = "footage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False, index=True)
    started_at = Column(DateTime, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)
    file_path = Column(String(1000), nullable=False)
    file_size_mb = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    resolution = Column(String(20), nullable=True)
    codec = Column(String(20), default="h265")
    bitrate_mbps = Column(Float, nullable=True)
    is_encrypted = Column(Boolean, default=True)
    checksum = Column(String(128), nullable=True)
    retention_until = Column(DateTime, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    alarm_id = Column(UUID(as_uuid=True), ForeignKey("alarms.id"), nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    camera = relationship("Camera", back_populates="footage_records")
