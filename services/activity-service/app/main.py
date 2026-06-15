<<<<<<< HEAD
import httpx
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.schemas import ActivityCreate
import app.repository as activity_repo

from app.infrastructure.rabbitmq_publisher import publish_activity_event

import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="activity-service", version="1.0.0")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
GAME_SERVICE_URL = os.getenv("GAME_SERVICE_URL", "http://localhost:8002")



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
=======
# activity-service — Module 3: Synchronous Communication
#
# This file wires the FastAPI app together and contains the two outbound
# HTTP helpers you must implement (see YOUR TASK below).
#
# To run:
#   uvicorn app.main:app --reload --port 8003

import httpx
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app import repository, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="activity-service")


# ---------------------------------------------------------------------------
# YOUR TASK — implement the two functions below
# ---------------------------------------------------------------------------

async def validate_user(user_id: str) -> None:
    """
    Verify that the user exists in user-service before logging an activity.

    Call: GET {settings.user_service_url}/v1/users/{user_id}

    Behaviour:
    - 200  → user exists, return normally (None)
    - 404  → raise HTTPException(status_code=404, detail="User not found")
    - Network error (httpx.RequestError) → retry the call once, then raise
             HTTPException(status_code=503, detail="user-service unavailable")
    - Any other non-2xx status → raise HTTPException(status_code=503, ...)

    Use `async with httpx.AsyncClient(timeout=5.0) as client:` for HTTP calls.
    This call is CRITICAL — the request must not proceed if validation fails.
    """
    raise NotImplementedError


async def fetch_game(game_id: str) -> dict | None:
    """
    Fetch game data from game-service to enrich the activity response.

    Call: GET {settings.game_service_url}/v1/games/{game_id}

    Behaviour:
    - 200  → return the response JSON as a dict
    - Any non-2xx status OR network error → return None (do NOT raise)

    This call is OPTIONAL — the activity is saved regardless of the result.
    Graceful degradation is the goal: the response will include "game": null
    when game-service is unreachable.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Endpoints — pre-written, they call your two functions above
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "activity-service"}


@app.post("/v1/activities", response_model=schemas.ActivityOut, status_code=201)
async def create_activity(data: schemas.ActivityCreate, db: Session = Depends(get_db)):
    await validate_user(data.user_id)
    activity = repository.create_activity(db, data)
    game_data = await fetch_game(activity.game_id)
    return {
        "id": activity.id,
        "user_id": activity.user_id,
        "action": activity.action,
        "duration_minutes": activity.duration_minutes,
        "created_at": activity.created_at,
        "game": game_data,
    }


@app.get("/v1/activities", response_model=schemas.ActivityList)
async def list_activities(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    activities, total = repository.list_activities(db, limit=limit, offset=offset)
    items = []
    for a in activities:
        game_data = await fetch_game(a.game_id)
        items.append({
            "id": a.id,
            "user_id": a.user_id,
            "action": a.action,
            "duration_minutes": a.duration_minutes,
            "created_at": a.created_at,
            "game": game_data,
        })
    return schemas.ActivityList(items=items, total=total, limit=limit, offset=offset)


@app.get("/v1/activities/user/{user_id}", response_model=schemas.ActivityList)
async def list_user_activities(
    user_id: str, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)
):
    activities, total = repository.list_user_activities(db, user_id, limit=limit, offset=offset)
    items = []
    for a in activities:
        game_data = await fetch_game(a.game_id)
        items.append({
            "id": a.id,
            "user_id": a.user_id,
            "action": a.action,
            "duration_minutes": a.duration_minutes,
            "created_at": a.created_at,
            "game": game_data,
        })
    return schemas.ActivityList(items=items, total=total, limit=limit, offset=offset)
>>>>>>> edcd48e1a2a7c6fcff9913d6467bc578de3d48c8
