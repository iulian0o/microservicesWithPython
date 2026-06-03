from pydantic import BaseModel
from typing import Literal
import uuid


class ActivityCreate(BaseModel):
    user_id: uuid.UUID
    game_id: uuid.UUID
    action: Literal["played", "completed", "reviewed", "wishlist_added"]
    duration_minutes: int | None = None