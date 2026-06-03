import httpx
from fastapi import FastAPI, HTTPException

USER_SERVICE_URL = "http://localhost:8001"
GAME_SERVICE_URL = "http://localhost:8002"

async def validate_user(user_id: str) -> None:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{USER_SERVICE_URL}/V1/users/{user_id}"
                )
            if resp.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )
            resp.raise_for_status()

            return
        
        except HTTPException:
            raise

        except httpx.RequestError:
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=503,
                    detail="user-service unavailable"
                )

async def fetch_game(game_id: str) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(
                f"{GAME_SERVICE_URL}/v1/games/{game_id}"
            )
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
