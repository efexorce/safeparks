import asyncio
import json
import logging
from typing import Optional, Callable, Awaitable, Dict, Any
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

TOPIC_MOTION = "safeparks/{camera_id}/motion"
TOPIC_EVENT = "safeparks/{camera_id}/event"
TOPIC_ENERGY = "safeparks/{camera_id}/energy"
TOPIC_BANDWIDTH = "safeparks/{camera_id}/bandwidth"
TOPIC_STATUS = "safeparks/{camera_id}/status"
TOPIC_COMMAND = "safeparks/{camera_id}/command"

try:
    import aiomqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logger.warning("aiomqtt not available")


class MQTTService:
    def __init__(self):
        self._client = None
        self._handlers: Dict[str, Callable[[str, Dict[str, Any]], Awaitable[None]]] = {}
        self._running = False

    def register_handler(
        self,
        topic_pattern: str,
        handler: Callable[[str, Dict[str, Any]], Awaitable[None]],
    ) -> None:
        self._handlers[topic_pattern] = handler

    async def start(self) -> None:
        if not MQTT_AVAILABLE:
            logger.warning("MQTT not available, service disabled")
            return
        self._running = True
        while self._running:
            try:
                async with aiomqtt.Client(
                    hostname=settings.MQTT_BROKER_HOST,
                    port=settings.MQTT_BROKER_PORT,
                    username=settings.MQTT_USERNAME,
                    password=settings.MQTT_PASSWORD,
                ) as client:
                    self._client = client
                    await client.subscribe("safeparks/#")
                    logger.info(f"MQTT connected: {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
                    async for message in client.messages:
                        await self._dispatch(str(message.topic), message.payload)
            except Exception as e:
                logger.error(f"MQTT connection error: {e}")
                if self._running:
                    await asyncio.sleep(5)

    async def stop(self) -> None:
        self._running = False

    async def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        if not MQTT_AVAILABLE or not self._client:
            logger.debug(f"MQTT publish skipped (unavailable): {topic}")
            return
        try:
            await self._client.publish(topic, json.dumps(payload))
        except Exception as e:
            logger.error(f"MQTT publish error: {e}")

    async def send_command(self, camera_id: str, command: str, params: Optional[Dict] = None) -> None:
        topic = TOPIC_COMMAND.format(camera_id=camera_id)
        payload = {
            "command": command,
            "params": params or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.publish(topic, payload)

    async def _dispatch(self, topic: str, payload: bytes) -> None:
        try:
            data = json.loads(payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.warning(f"Invalid MQTT payload on topic {topic}")
            return

        for pattern, handler in self._handlers.items():
            if self._matches(pattern, topic):
                try:
                    await handler(topic, data)
                except Exception as e:
                    logger.error(f"MQTT handler error for {topic}: {e}")

    @staticmethod
    def _matches(pattern: str, topic: str) -> bool:
        pattern_parts = pattern.split("/")
        topic_parts = topic.split("/")
        if len(pattern_parts) != len(topic_parts):
            return False
        for p, t in zip(pattern_parts, topic_parts):
            if p == "#":
                return True
            if p != "+" and p != t:
                return False
        return True


mqtt_service = MQTTService()
