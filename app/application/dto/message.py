import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator


class SendMessageRequest(BaseModel):
    receiver_id: uuid.UUID
    content: str
    contract_id: uuid.UUID | None = None

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class MessageResponse(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    content: str
    is_read: bool
    contract_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    interlocutor_id: str
    last_message: str
    last_message_at: str
    is_read: bool


class UnreadCountResponse(BaseModel):
    unread_count: int
