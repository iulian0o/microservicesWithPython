<<<<<<< HEAD
from pydantic import BaseModel
from typing import Literal
import uuid


class ActivityCreate(BaseModel):
    user_id: uuid.UUID
    game_id: uuid.UUID
    action: Literal["played", "completed", "reviewed", "wishlist_added"]
    duration_minutes: int | None = None
=======
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GameSummary(BaseModel):
    """Embedded game data returned by game-service. Matches GET /v1/games/{id}."""
    id: str
    title: str
    genre: str
    platform: str
    cover_url: Optional[str] = None


class ActivityCreate(BaseModel):
    user_id: str
    game_id: str
    action: str  # played | completed | reviewed | wishlist_added
    duration_minutes: Optional[int] = None


class ActivityOut(BaseModel):
    id: str
    user_id: str
    action: str
    duration_minutes: Optional[int]
    created_at: datetime
    game: Optional[GameSummary] = None  # null when game-service is unreachable

    model_config = {"from_attributes": True}


class ActivityList(BaseModel):
    """Paginated envelope — all list endpoints return this shape."""
    items: list[ActivityOut]
    total: int
    limit: int
    offset: int
>>>>>>> edcd48e1a2a7c6fcff9913d6467bc578de3d48c8
