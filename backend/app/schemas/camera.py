from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.camera import CameraStatus, CameraQualityMode, AIStatus


class CameraBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location_name: str = Field(..., min_length=1, max_length=500)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    ip_address: Optional[str] = None
    rtsp_url: Optional[str] = None
    mac_address: Optional[str] = None
    park_zone: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    edge_device_type: Optional[str] = None
    edge_device_ip: Optional[str] = None
    poe_enabled: bool = True
    solar_panel_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ip_address: Optional[str] = None
    rtsp_url: Optional[str] = None
    status: Optional[CameraStatus] = None
    quality_mode: Optional[CameraQualityMode] = None
    ai_status: Optional[AIStatus] = None
    is_active: Optional[bool] = None
    solar_panel_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class CameraResponse(CameraBase):
    id: UUID
    status: CameraStatus
    quality_mode: CameraQualityMode
    ai_status: AIStatus
    current_fps: int
    current_bitrate_mbps: float
    current_resolution: str
    motion_detected: bool
    last_motion_at: Optional[datetime]
    is_active: bool
    installed_at: datetime
    last_seen_at: Optional[datetime]
    monthly_data_used_gb: float
    daily_data_used_gb: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CameraListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    cameras: List[CameraResponse]


class CameraEventResponse(BaseModel):
    id: UUID
    camera_id: UUID
    event_type: str
    occurred_at: datetime
    confidence_score: Optional[float]
    bounding_box: Optional[Dict[str, Any]]
    frame_path: Optional[str]
    is_false_positive: bool
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class BandwidthUsageResponse(BaseModel):
    id: UUID
    camera_id: UUID
    recorded_at: datetime
    bytes_sent: float
    bytes_received: float
    duration_seconds: int
    quality_mode: Optional[str]

    class Config:
        from_attributes = True


class CameraStatsResponse(BaseModel):
    camera_id: UUID
    total_cameras: int
    online_cameras: int
    offline_cameras: int
    sleep_cameras: int
    total_daily_data_gb: float
    total_monthly_data_gb: float
    active_alarms: int
    average_ai_confidence: Optional[float]
