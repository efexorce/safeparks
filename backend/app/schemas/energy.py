from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.energy import PowerSource


class EnergyReadingCreate(BaseModel):
    camera_id: Optional[UUID] = None
    solar_panel_id: Optional[UUID] = None
    power_consumption_w: float = Field(..., ge=0.0)
    power_source: PowerSource = PowerSource.POE
    solar_output_w: Optional[float] = None
    battery_level_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    voltage: Optional[float] = None
    current_ampere: Optional[float] = None
    temperature_celsius: Optional[float] = None
    is_sleep_mode: bool = False
    metadata: Optional[Dict[str, Any]] = None


class EnergyReadingResponse(BaseModel):
    id: UUID
    camera_id: Optional[UUID]
    solar_panel_id: Optional[UUID]
    recorded_at: datetime
    power_consumption_w: float
    power_source: PowerSource
    solar_output_w: Optional[float]
    battery_level_percent: Optional[float]
    voltage: Optional[float]
    current_ampere: Optional[float]
    is_sleep_mode: bool
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class SolarPanelResponse(BaseModel):
    id: UUID
    name: str
    location_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    capacity_watts: float
    current_output_watts: float
    battery_capacity_wh: Optional[float]
    battery_level_percent: float
    is_active: bool
    installed_at: datetime
    last_reading_at: Optional[datetime]

    class Config:
        from_attributes = True


class CityEnergyStats(BaseModel):
    total_consumption_kw: float
    total_solar_output_kw: float
    solar_ratio_percent: float
    cameras_in_sleep: int
    total_cameras: int
    energy_saved_kwh: float
    cost_saved_usd: Optional[float]
    by_district: Dict[str, Dict[str, float]]
