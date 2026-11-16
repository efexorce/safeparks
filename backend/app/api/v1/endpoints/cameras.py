from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from app.db.session import get_db
from app.services.camera_service import CameraService
from app.schemas.camera import (
    CameraCreate, CameraUpdate, CameraResponse,
    CameraListResponse, CameraStatsResponse
)
from app.models.camera import CameraStatus

router = APIRouter()


@router.get("/", response_model=CameraListResponse)
async def list_cameras(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: Optional[CameraStatus] = None,
    district: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
):
    service = CameraService(db)
    cameras, total = await service.get_cameras(page, page_size, status, district, is_active)
    return CameraListResponse(total=total, page=page, page_size=page_size, cameras=cameras)


@router.post("/", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    data: CameraCreate,
    db: AsyncSession = Depends(get_db),
):
    service = CameraService(db)
    camera = await service.create_camera(data)
    return camera


@router.get("/map", response_model=List[dict])
async def get_map_data(db: AsyncSession = Depends(get_db)):
    service = CameraService(db)
    return await service.get_map_data()


@router.get("/stats", response_model=dict)
async def get_summary_stats(db: AsyncSession = Depends(get_db)):
    service = CameraService(db)
    return await service.get_summary_stats()


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = CameraService(db)
    camera = await service.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: UUID,
    data: CameraUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = CameraService(db)
    camera = await service.update_camera(camera_id, data)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = CameraService(db)
    deleted = await service.delete_camera(camera_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Camera not found")


@router.post("/{camera_id}/motion", response_model=CameraResponse)
async def update_motion_status(
    camera_id: UUID,
    motion_detected: bool,
    db: AsyncSession = Depends(get_db),
):
    service = CameraService(db)
    camera = await service.update_motion_status(camera_id, motion_detected)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.get("/{camera_id}/bandwidth", response_model=dict)
async def get_bandwidth_quota(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = CameraService(db)
    return await service.check_bandwidth_quota(camera_id)
