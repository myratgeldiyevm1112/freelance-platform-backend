import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SkillEntity:
    id: uuid.UUID
    name: str
    created_at: datetime


@dataclass
class UserSkillEntity:
    id: uuid.UUID
    user_id: uuid.UUID
    skill_id: uuid.UUID
    skill_name: str
    created_at: datetime