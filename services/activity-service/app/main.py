import httpx
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.schemas import ActivityCreate
import app.repository as activity_repo

from app.infrastructure.rabbitmq_publisher import publish_activity_event

Base.metadata.create_all(bind=engine)

app = FastAPI(title="activity-service", version="1.0.0")

USER_SERVICE_URL = "http://localhost:8001"
GAME_SERVICE_URL = "http://localhost:8002"



async def validate_user(user_id: str) -> None:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{USER_SERVICE_URL}/v1/users/{user_id}")
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found")
            resp.raise_for_status()
            return
        except HTTPException:
            raise
        except httpx.RequestError:
            if attempt == max_retries - 1:
                raise HTTPException(status_code=503, detail="user-service unavailable")


async def fetch_game(game_id: str) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{GAME_SERVICE_URL}/v1/games/{game_id}")
        if not resp.is_success:
            return None
        data = resp.json()
        return {
            "id":        data["id"],
            "title":     data["title"],
            "genre":     data["genre"],
            "platform":  data["platform"],
            "cover_url": data.get("cover_url"),
        }
    except Exception:
        return None


def _serialize(activity, game: dict | None) -> dict:
    return {
        "id":               activity.id,
        "user_id":          activity.user_id,
        "action":           activity.action,
        "duration_minutes": activity.duration_minutes,
        "created_at":       activity.created_at.isoformat() + "Z",
        "game":             game,
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "activity-service"}


@app.post("/v1/activities", status_code=201)
async def create_activity(
    payload: ActivityCreate,
    db: Session = Depends(get_db),
):
    await validate_user(str(payload.user_id))
    activity = activity_repo.create(db, payload)
    game = await fetch_game(str(payload.game_id))
    game_title = game["title"] if game else None

    await publish_activity_event(
        user_id = str(payload.user_id),
        game_id = str(payload.game_id),
        action = payload.action,
        game_title = game_title
    )

    return _serialize(activity, game)


@app.get("/v1/activities")
async def list_activities(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = activity_repo.list_activities(db, limit=limit, offset=offset)
    enriched = []
    for a in items:
        game = await fetch_game(a.game_id)
        enriched.append(_serialize(a, game))
    return {"items": enriched, "total": total, "limit": limit, "offset": offset}


@app.get("/v1/activities/user/{user_id}")
async def list_activities_by_user(
    user_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = activity_repo.list_by_user(db, user_id=user_id, limit=limit, offset=offset)
    enriched = []
    for a in items:
        game = await fetch_game(a.game_id)
        enriched.append(_serialize(a, game))
    return {"items": enriched, "total": total, "limit": limit, "offset": offset}