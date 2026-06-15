<<<<<<< HEAD
from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime, timezone
import uuid
=======
from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, DateTime, Integer, String

>>>>>>> edcd48e1a2a7c6fcff9913d6467bc578de3d48c8
from app.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    game_id = Column(String, nullable=False)
<<<<<<< HEAD
    action = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
=======
    action = Column(String, nullable=False)  # played | completed | reviewed | wishlist_added
    duration_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
>>>>>>> edcd48e1a2a7c6fcff9913d6467bc578de3d48c8
