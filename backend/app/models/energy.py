import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Boolean, DateTime,
    ForeignKey, Enum as SAEnum, JSON, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.db.session import Base


class PowerSource(str, enum.Enum):
    SOLAR = "solar"
    POE = "poe"
    GRID = "grid"
    BATTERY = "battery"
    HYBRID = "hybrid"


class SolarPanel(Base):
    __tablename__ = "solar_panels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    location_name = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    capacity_watts = Column(Float, nullable=False)
    current_output_watts = Column(Float, default=0.0)
    battery_capacity_wh = Column(Float, nullable=True)
    battery_level_percent = Column(Float, default=100.0)
    is_active = Column(Boolean, default=True)
    installed_at = Column(DateTime, default=datetime.utcnow)
    last_reading_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cameras = relationship("Camera", back_populates="solar_panel")
    energy_readings = relationship("EnergyReading", back_populates="solar_panel")


class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=True, index=True)
    solar_panel_id = Column(UUID(as_uuid=True), ForeignKey("solar_panels.id"), nullable=True, index=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    power_consumption_w = Column(Float, nullable=False)
    power_source = Column(SAEnum(PowerSource), default=PowerSource.POE, nullable=False)
    solar_output_w = Column(Float, nullable=True)
    battery_level_percent = Column(Float, nullable=True)
    voltage = Column(Float, nullable=True)
    current_ampere = Column(Float, nullable=True)
    temperature_celsius = Column(Float, nullable=True)
    is_sleep_mode = Column(Boolean, default=False)
    metadata = Column(JSON, nullable=True)

    camera = relationship("Camera", back_populates="energy_readings")
    solar_panel = relationship("SolarPanel", back_populates="energy_readings")
