"""
Lead capture and management routes.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.services.lead_capture_service import LeadCaptureService

router = APIRouter()

_leads = LeadCaptureService()


class ManualLeadRequest(BaseModel):
    first_name: str
    last_name: str = ""
    email: str = ""
    phone: str = ""
    source: str = "manual"
    notes: str = ""

class LeadFormData(BaseModel):
    leadgen_id: str
    form_id: str
    page_id: str
    field_data: List[Dict[str, Any]]


@router.post("/capture")
async def capture_lead(req: ManualLeadRequest):
    return await _leads.capture_lead(
        lead_data={
            "first_name": req.first_name,
            "last_name": req.last_name,
            "email": req.email,
            "phone": req.phone,
            "source": req.source,
            "comment_text": req.notes,
        }
    )

@router.post("/from-form")
async def capture_from_form(req: LeadFormData):
    return await _leads.capture_from_lead_form(req.model_dump())

@router.post("/sync")
async def sync_to_gymbot():
    """Push all pending leads to GymBot's SQLite database."""
    return await _leads.sync_pending_leads()

@router.get("/recent")
async def recent_leads(limit: int = Query(50, ge=1, le=200)):
    return await _leads.get_leads(limit=limit)
