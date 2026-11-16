import logging
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from app.core.config import settings
from app.models.alarm import Alarm, AlarmSeverity

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.websocket_clients: List = []

    async def send_alarm_notification(self, alarm: Alarm, camera_name: str) -> bool:
        tasks = [
            self._notify_websocket(alarm, camera_name),
        ]
        if settings.SMTP_HOST and alarm.severity in [AlarmSeverity.CRITICAL, AlarmSeverity.HIGH]:
            tasks.append(self._send_email_notification(alarm, camera_name))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = all(not isinstance(r, Exception) for r in results)
        latency_ms = (datetime.utcnow() - alarm.triggered_at).total_seconds() * 1000
        logger.info(
            f"Notification sent for alarm {alarm.id}: latency={latency_ms:.1f}ms success={success}"
        )
        return success

    async def _notify_websocket(self, alarm: Alarm, camera_name: str) -> None:
        payload = {
            "type": "alarm",
            "data": {
                "id": str(alarm.id),
                "camera_id": str(alarm.camera_id),
                "camera_name": camera_name,
                "alarm_type": alarm.alarm_type,
                "severity": alarm.severity,
                "status": alarm.status,
                "location_name": alarm.location_name,
                "latitude": alarm.latitude,
                "longitude": alarm.longitude,
                "triggered_at": alarm.triggered_at.isoformat(),
                "confidence_score": alarm.confidence_score,
                "thumbnail_path": alarm.thumbnail_path,
            },
        }
        for client in self.websocket_clients[:]:
            try:
                await client.send_text(json.dumps(payload))
            except Exception:
                self.websocket_clients.remove(client)

    async def _send_email_notification(self, alarm: Alarm, camera_name: str) -> None:
        if not settings.SMTP_HOST:
            return
        recipients = [r.strip() for r in settings.ALERT_EMAIL_RECIPIENTS.split(",") if r.strip()]
        if not recipients:
            return
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[SafeParks ALERT] {alarm.alarm_type.upper()} - {camera_name}"
        msg["From"] = settings.SMTP_USER or "noreply@safeparks.local"
        msg["To"] = ", ".join(recipients)
        body = f"""
        SafeParks Güvenlik Alarmı

        Tür: {alarm.alarm_type}
        Şiddet: {alarm.severity}
        Kamera: {camera_name}
        Konum: {alarm.location_name}
        Zaman: {alarm.triggered_at.isoformat()}
        Güven Skoru: {alarm.confidence_score:.2%} if alarm.confidence_score else 'N/A'
        """
        msg.attach(MIMEText(body, "plain"))
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._send_smtp, msg, recipients)

    def _send_smtp(self, msg: MIMEMultipart, recipients: List[str]) -> None:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(msg["From"], recipients, msg.as_string())

    def register_websocket(self, websocket) -> None:
        self.websocket_clients.append(websocket)

    def unregister_websocket(self, websocket) -> None:
        if websocket in self.websocket_clients:
            self.websocket_clients.remove(websocket)


notification_service = NotificationService()
