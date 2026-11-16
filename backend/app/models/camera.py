import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, Boolean,
    DateTime, ForeignKey, Enum as SAEnum, Text, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.db.session import Base


class CameraStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    SLEEP = "sleep"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class CameraQualityMode(str, enum.Enum):
    HIGH = "high"
    LOW = "low"
    ADAPTIVE = "adaptive"


class AIStatus(str, enum.Enum):
    ACTIVE = "active"
    SLEEP = "sleep"
    DISABLED = "disabled"


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    location_name = Column(String(500), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    ip_address = Column(String(50), nullable=True)
    rtsp_url = Column(String(500), nullable=True)
    mac_address = Column(String(17), nullable=True, unique=True)
    status = Column(SAEnum(CameraStatus), default=CameraStatus.OFFLINE, nullable=False)
    quality_mode = Column(SAEnum(CameraQualityMode), default=CameraQualityMode.ADAPTIVE, nullable=False)
    ai_status = Column(SAEnum(AIStatus), default=AIStatus.SLEEP, nullable=False)
    current_fps = Column(Integer, default=5)
    current_bitrate_mbps = Column(Float, default=0.8)
    current_resolution = Column(String(20), default="480p")
    motion_detected = Column(Boolean, default=False)
    last_motion_at = Column(DateTime, nullable=True)
    poe_enabled = Column(Boolean, default=True)
    solar_panel_id = Column(UUID(as_uuid=True), ForeignKey("solar_panels.id"), nullable=True)
    edge_device_type = Column(String(100), nullable=True)
    edge_device_ip = Column(String(50), nullable=True)
    park_zone = Column(String(255), nullable=True)
    district = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    installed_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, nullable=True)
    monthly_data_used_gb = Column(Float, default=0.0)
    daily_data_used_gb = Column(Float, default=0.0)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    events = relationship("CameraEvent", back_populates="camera", lazy="dynamic")
    alarms = relationship("Alarm", back_populates="camera", lazy="dynamic")
    energy_readings = relationship("EnergyReading", back_populates="camera", lazy="dynamic")
    solar_panel = relationship("SolarPanel", back_populates="cameras")
    footage_records = relationship("FootageRecord", back_populates="camera", lazy="dynamic")
    bandwidth_usage = relationship("BandwidthUsage", back_populates="camera", lazy="dynamic")


class CameraEvent(Base):
    __tablename__ = "camera_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    confidence_score = Column(Float, nullable=True)
    bounding_box = Column(JSON, nullable=True)
    frame_path = Column(String(500), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    is_false_positive = Column(Boolean, default=False)
    metadata = Column(JSON, nullable=True)

    camera = relationship("Camera", back_populates="events")
    alarm = relationship("Alarm", back_populates="event", uselist=False)


class BandwidthUsage(Base):
    __tablename__ = "bandwidth_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False, index=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    bytes_sent = Column(Float, default=0.0)
    bytes_received = Column(Float, default=0.0)
    duration_seconds = Column(Integer, default=60)
    quality_mode = Column(String(20), nullable=True)

    camera = relationship("Camera", back_populates="bandwidth_usage")
