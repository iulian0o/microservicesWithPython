# Entry point — FastAPI application.
#
# Create the FastAPI app instance and register the router from app.routes.
# Keep it minimal: no business logic, no endpoints defined here.
#
# To run the service locally:
#   uvicorn app.main:app --reload --port 8002
#
# Then open: http://localhost:8002/docs

from fastapi import FastAPI

from app.database import Base, engine
from app.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="game-service")
app.include_router(router)