from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.notification_service import notification_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    notification_service.register_websocket(websocket)
    logger.info(f"WebSocket client connected: {websocket.client}")
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        notification_service.unregister_websocket(websocket)
        logger.info(f"WebSocket client disconnected: {websocket.client}")
