"""
Content scheduler management routes.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.content_scheduler_service import ContentSchedulerService

router = APIRouter()

_scheduler = ContentSchedulerService()


class ScheduleRequest(BaseModel):
    content_id: int
    publish_at: str  # ISO 8601
    platform: str = "facebook"

class CancelRequest(BaseModel):
    schedule_id: int


@router.post("/schedule")
async def schedule_content(req: ScheduleRequest, db: AsyncSession = Depends(get_db)):
    publish_time = datetime.fromisoformat(req.publish_at)
    return await _scheduler.schedule_content(
        db=db,
        content_id=req.content_id,
        publish_at=publish_time,
        platform=req.platform,
    )

@router.delete("/schedule/{schedule_id}")
async def cancel_scheduled(schedule_id: int, db: AsyncSession = Depends(get_db)):
    return await _scheduler.cancel_scheduled(db, schedule_id)

@router.get("/queue")
async def get_queue(db: AsyncSession = Depends(get_db)):
    return await _scheduler.get_queue(db)

@router.get("/optimal-times")
async def optimal_times():
    return _scheduler.get_optimal_times()
