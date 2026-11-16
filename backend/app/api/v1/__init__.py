from fastapi import APIRouter
from app.api.v1.endpoints import cameras, alarms, energy, auth, reports, websocket

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["Cameras"])
api_router.include_router(alarms.router, prefix="/alarms", tags=["Alarms"])
api_router.include_router(energy.router, prefix="/energy", tags=["Energy"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(websocket.router, tags=["WebSocket"])
