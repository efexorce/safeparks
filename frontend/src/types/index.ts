export type CameraStatus = 'online' | 'offline' | 'sleep' | 'maintenance' | 'error'
export type AIStatus = 'active' | 'sleep' | 'disabled'
export type QualityMode = 'high' | 'low' | 'adaptive'

export interface Camera {
  id: string
  name: string
  location_name: string
  latitude: number
  longitude: number
  status: CameraStatus
  ai_status: AIStatus
  quality_mode: QualityMode
  current_fps: number
  current_bitrate_mbps: number
  current_resolution: string
  motion_detected: boolean
  last_motion_at: string | null
  poe_enabled: boolean
  park_zone: string | null
  district: string | null
  city: string | null
  daily_data_used_gb: number
  monthly_data_used_gb: number
  is_active: boolean
  installed_at: string
  last_seen_at: string | null
}

export type AlarmType = 'vandalism' | 'fight' | 'person_down' | 'suspicious_object' | 'intrusion' | 'fire' | 'flood' | 'unknown'
export type AlarmSeverity = 'low' | 'medium' | 'high' | 'critical'
export type AlarmStatus = 'pending' | 'acknowledged' | 'investigating' | 'resolved' | 'false_positive'

export interface Alarm {
  id: string
  camera_id: string
  alarm_type: AlarmType
  severity: AlarmSeverity
  status: AlarmStatus
  confidence_score: number | null
  description: string | null
  thumbnail_path: string | null
  triggered_at: string
  acknowledged_at: string | null
  resolved_at: string | null
  location_name: string | null
  latitude: number | null
  longitude: number | null
  detection_latency_ms: number | null
}

export interface EnergyStats {
  total_consumption_kw: number
  total_solar_output_kw: number
  solar_ratio_percent: number
  cameras_in_sleep: number
  total_cameras: number
  energy_saved_kwh: number
  cost_saved_usd: number | null
}

export interface CameraStats {
  total_cameras: number
  online_cameras: number
  offline_cameras: number
  sleep_cameras: number
  total_daily_data_gb: number
  total_monthly_data_gb: number
}

export interface AlarmSummary {
  total: number
  pending: number
  acknowledged: number
  resolved: number
  false_positives: number
}

export interface MapCamera {
  id: string
  name: string
  latitude: number
  longitude: number
  status: CameraStatus
  ai_status: AIStatus
  motion_detected: boolean
  district: string | null
  park_zone: string | null
  daily_data_used_gb: number
  current_resolution: string
}

export interface WebSocketMessage {
  type: 'alarm' | 'camera_status' | 'energy'
  data: Record<string, unknown>
}
