"""
Messenger conversation routes — view threads, send messages.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.messenger_service import MessengerService
from app.services.credential_resolver import get_facebook_credentials

router = APIRouter()


async def _messenger(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessengerService:
    creds = await get_facebook_credentials(db, user_id=current_user.id)
    return MessengerService(page_id=creds.page_id, page_token=creds.page_token)


class SendMessageRequest(BaseModel):
    recipient_id: str
    text: str


@router.get("/conversations")
async def list_conversations(msngr: MessengerService = Depends(_messenger), limit: int = Query(25, ge=1, le=100)):
    return await msngr.get_conversations(limit=limit)

@router.get("/conversations/{conversation_id}/messages")
async def list_messages(conversation_id: str, msngr: MessengerService = Depends(_messenger), limit: int = Query(20, ge=1, le=100)):
    return await msngr.get_messages(conversation_id, limit=limit)

@router.post("/send")
async def send_message(req: SendMessageRequest, msngr: MessengerService = Depends(_messenger)):
    return await msngr.send_message(req.recipient_id, req.text)
