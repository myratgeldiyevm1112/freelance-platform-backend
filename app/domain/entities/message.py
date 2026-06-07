import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MessageEntity:
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    content: str
    is_read: bool
    created_at: datetime
    updated_at: datetime
    contract_id: uuid.UUID | None = None
