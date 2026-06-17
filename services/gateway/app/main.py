import httpx
from fastapi import FastAPI, Request, Response
from jose import JWTError, jwt

from app.config import settings

app = FastAPI(title="gateway", version="1.0.0")

ROUTES: dict[str, str] = {
    "users":      settings.user_service_url,
    "games":      settings.game_service_url,
    "activities": settings.activity_service_url,
    "notifications": settings.notification_service_url,
    "consent": settings.logging_service_url,
    "logs": settings.logging_service_url,
    # Added in Module 6
    "auth": settings.auth_service_url,
}

# Paths that must remain public — no token required.
PUBLIC_PATHS = {"v1/auth/token"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(request: Request, path: str):
    segments = path.split("/")
    if len(segments) < 2:
        return Response(status_code=404, content="Not found")

    resource = segments[1]
    target_base = ROUTES.get(resource)

    print(f"DEBUG path={path!r} resource={resource!r} target_base={target_base!r}")

    if target_base is None:
        return Response(status_code=404, content=f"Unknown resource: {resource}")

    # JWT validation — skip only for the public token endpoint.
    if path not in PUBLIC_PATHS:
        auth_header = request.headers.get("authorization")
        print(f"DEBUG auth_header={auth_header!r}")
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(status_code=401, content="Missing or invalid token")

        token = auth_header.split(" ", 1)[1]
        try:
            jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        except JWTError:
            return Response(status_code=401, content="Missing or invalid token")

    target_url = f"{target_base}/{path}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=request.headers.raw,
                content=await request.body(),
                params=request.query_params,
            )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type"),
        )

    except httpx.RequestError:
        return Response(status_code=503, content="Service unavailable")