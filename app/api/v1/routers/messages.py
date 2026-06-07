import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.message import SendMessageRequest, MessageResponse, ConversationResponse, UnreadCountResponse
from app.application.use_cases.send_message import SendMessage
from app.application.use_cases.get_messages import GetMessages, GetConversations, GetUnreadCount
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.message_repository import MessageRepository

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/", response_model=MessageResponse, status_code=201)
async def send_message(
    data: SendMessageRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = SendMessage(MessageRepository(db))
    return await use_case.execute(
        current_user=current_user,
        receiver_id=data.receiver_id,
        content=data.content,
        contract_id=data.contract_id,
    )


@router.get("/conversations", response_model=list[ConversationResponse])
async def get_conversations(
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetConversations(MessageRepository(db))
    return await use_case.execute(current_user)


@router.get("/conversations/{interlocutor_id}", response_model=list[MessageResponse])
async def get_conversation(
    interlocutor_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetMessages(MessageRepository(db))
    return await use_case.execute(
        current_user=current_user,
        interlocutor_id=interlocutor_id,
        limit=limit,
        offset=offset,
    )


@router.get("/unread", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetUnreadCount(MessageRepository(db))
    return await use_case.execute(current_user)
