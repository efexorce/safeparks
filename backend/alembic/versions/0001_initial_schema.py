"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(500), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), nullable=False, default="viewer"),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_superuser", sa.Boolean, default=False),
        sa.Column("last_login_at", sa.DateTime, nullable=True),
        sa.Column("failed_login_attempts", sa.Integer, default=0),
        sa.Column("locked_until", sa.DateTime, nullable=True),
        sa.Column("notification_preferences", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )

    op.create_table(
        "solar_panels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("location_name", sa.String(500), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("capacity_watts", sa.Float, nullable=False),
        sa.Column("current_output_watts", sa.Float, default=0.0),
        sa.Column("battery_capacity_wh", sa.Float, nullable=True),
        sa.Column("battery_level_percent", sa.Float, default=100.0),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("installed_at", sa.DateTime),
        sa.Column("last_reading_at", sa.DateTime, nullable=True),
        sa.Column("metadata", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime),
    )

    op.create_table(
        "cameras",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("location_name", sa.String(500), nullable=False),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("rtsp_url", sa.String(500), nullable=True),
        sa.Column("mac_address", sa.String(17), nullable=True, unique=True),
        sa.Column("status", sa.String(50), default="offline"),
        sa.Column("quality_mode", sa.String(50), default="adaptive"),
        sa.Column("ai_status", sa.String(50), default="sleep"),
        sa.Column("current_fps", sa.Integer, default=5),
        sa.Column("current_bitrate_mbps", sa.Float, default=0.8),
        sa.Column("current_resolution", sa.String(20), default="480p"),
        sa.Column("motion_detected", sa.Boolean, default=False),
        sa.Column("last_motion_at", sa.DateTime, nullable=True),
        sa.Column("poe_enabled", sa.Boolean, default=True),
        sa.Column("solar_panel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("solar_panels.id"), nullable=True),
        sa.Column("edge_device_type", sa.String(100), nullable=True),
        sa.Column("edge_device_ip", sa.String(50), nullable=True),
        sa.Column("park_zone", sa.String(255), nullable=True),
        sa.Column("district", sa.String(255), nullable=True),
        sa.Column("city", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("installed_at", sa.DateTime),
        sa.Column("last_seen_at", sa.DateTime, nullable=True),
        sa.Column("monthly_data_used_gb", sa.Float, default=0.0),
        sa.Column("daily_data_used_gb", sa.Float, default=0.0),
        sa.Column("metadata", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )
    op.create_index("ix_cameras_status", "cameras", ["status"])
    op.create_index("ix_cameras_district", "cameras", ["district"])

    op.create_table(
        "camera_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id"), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("occurred_at", sa.DateTime, nullable=False),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("bounding_box", postgresql.JSON, nullable=True),
        sa.Column("frame_path", sa.String(500), nullable=True),
        sa.Column("processed_at", sa.DateTime, nullable=True),
        sa.Column("is_false_positive", sa.Boolean, default=False),
        sa.Column("metadata", postgresql.JSON, nullable=True),
    )
    op.create_index("ix_camera_events_camera_id", "camera_events", ["camera_id"])
    op.create_index("ix_camera_events_occurred_at", "camera_events", ["occurred_at"])

    op.create_table(
        "alarms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id"), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("camera_events.id"), nullable=True),
        sa.Column("alarm_type", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), default="pending"),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("thumbnail_path", sa.String(500), nullable=True),
        sa.Column("clip_path", sa.String(500), nullable=True),
        sa.Column("triggered_at", sa.DateTime, nullable=False),
        sa.Column("acknowledged_at", sa.DateTime, nullable=True),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
        sa.Column("acknowledged_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("detection_latency_ms", sa.Float, nullable=True),
        sa.Column("notification_sent", sa.Boolean, default=False),
        sa.Column("notification_sent_at", sa.DateTime, nullable=True),
        sa.Column("false_positive_reason", sa.Text, nullable=True),
        sa.Column("location_name", sa.String(500), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("metadata", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )
    op.create_index("ix_alarms_camera_id", "alarms", ["camera_id"])
    op.create_index("ix_alarms_triggered_at", "alarms", ["triggered_at"])
    op.create_index("ix_alarms_status", "alarms", ["status"])

    op.create_table(
        "alarm_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("alarm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("alarms.id"), nullable=False),
        sa.Column("triggered_at", sa.DateTime, nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("performed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSON, nullable=True),
    )

    op.create_table(
        "energy_readings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id"), nullable=True),
        sa.Column("solar_panel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("solar_panels.id"), nullable=True),
        sa.Column("recorded_at", sa.DateTime, nullable=False),
        sa.Column("power_consumption_w", sa.Float, nullable=False),
        sa.Column("power_source", sa.String(50), nullable=False),
        sa.Column("solar_output_w", sa.Float, nullable=True),
        sa.Column("battery_level_percent", sa.Float, nullable=True),
        sa.Column("voltage", sa.Float, nullable=True),
        sa.Column("current_ampere", sa.Float, nullable=True),
        sa.Column("temperature_celsius", sa.Float, nullable=True),
        sa.Column("is_sleep_mode", sa.Boolean, default=False),
        sa.Column("metadata", postgresql.JSON, nullable=True),
    )
    op.create_index("ix_energy_readings_camera_id", "energy_readings", ["camera_id"])
    op.create_index("ix_energy_readings_recorded_at", "energy_readings", ["recorded_at"])

    op.create_table(
        "bandwidth_usage",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id"), nullable=False),
        sa.Column("recorded_at", sa.DateTime, nullable=False),
        sa.Column("bytes_sent", sa.Float, default=0.0),
        sa.Column("bytes_received", sa.Float, default=0.0),
        sa.Column("duration_seconds", sa.Integer, default=60),
        sa.Column("quality_mode", sa.String(20), nullable=True),
    )
    op.create_index("ix_bandwidth_usage_camera_id", "bandwidth_usage", ["camera_id"])
    op.create_index("ix_bandwidth_usage_recorded_at", "bandwidth_usage", ["recorded_at"])

    op.create_table(
        "footage_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id"), nullable=False),
        sa.Column("started_at", sa.DateTime, nullable=False),
        sa.Column("ended_at", sa.DateTime, nullable=True),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("file_size_mb", sa.Float, nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        sa.Column("resolution", sa.String(20), nullable=True),
        sa.Column("codec", sa.String(20), default="h265"),
        sa.Column("bitrate_mbps", sa.Float, nullable=True),
        sa.Column("is_encrypted", sa.Boolean, default=True),
        sa.Column("checksum", sa.String(128), nullable=True),
        sa.Column("retention_until", sa.DateTime, nullable=False),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("alarm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("alarms.id"), nullable=True),
        sa.Column("metadata", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime),
    )
    op.create_index("ix_footage_records_camera_id", "footage_records", ["camera_id"])
    op.create_index("ix_footage_records_started_at", "footage_records", ["started_at"])


def downgrade() -> None:
    op.drop_table("footage_records")
    op.drop_table("bandwidth_usage")
    op.drop_table("energy_readings")
    op.drop_table("alarm_logs")
    op.drop_table("alarms")
    op.drop_table("camera_events")
    op.drop_table("cameras")
    op.drop_table("solar_panels")
    op.drop_table("users")
