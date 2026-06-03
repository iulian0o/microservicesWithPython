# Module 2 exercise — write your pytest tests here.
#
# Use FastAPI's TestClient to test your endpoints without a running server.
#
# Suggested test cases:
# - POST /v1/games/ with valid data returns 201 and a GameOut body
# - GET  /v1/games/{id} with a valid ID returns 200 and the correct game
# - GET  /v1/games/{id} with an unknown ID returns 404
# - GET  /v1/games/ returns a GameList with the correct total
# - GET  /v1/games/search?q=... returns only matching games
#
# Tip: use an in-memory SQLite database in your test fixture so tests
# never touch the real games.db file.
#
# Run tests with:
#   pytest tests/

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_games.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

SAMPLE_GAME = {
    "title": "The Legend of Zelda",
    "genre": "Adventure",
    "platform": "Nintendo Switch",
    "release_year": 2017,
    "cover_url": "https://example.com/zelda.jpg",
}


def test_create_game_returns_201():
    response = client.post("/v1/games/", json=SAMPLE_GAME)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "The Legend of Zelda"
    assert data["genre"] == "Adventure"
    assert data["release_year"] == 2017
    assert "id" in data


def test_create_game_without_optional_fields():
    response = client.post("/v1/games/", json={
        "title": "Tetris",
        "genre": "Puzzle",
        "platform": "Game Boy",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["release_year"] is None
    assert data["cover_url"] is None


def test_create_game_missing_required_field_returns_422():
    response = client.post("/v1/games/", json={
        "title": "Tetris",
    })
    assert response.status_code == 422


def test_list_games_empty():
    response = client.get("/v1/games/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_games_after_create():
    client.post("/v1/games/", json=SAMPLE_GAME)
    client.post("/v1/games/", json={
        "title": "Super Mario",
        "genre": "Platformer",
        "platform": "Nintendo Switch",
    })

    data = client.get("/v1/games/").json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_games_pagination():
    for i in range(5):
        client.post("/v1/games/", json={
            "title": f"Game {i}",
            "genre": "Action",
            "platform": "PC",
        })

    data = client.get("/v1/games/?limit=2&offset=0").json()
    assert data["total"] == 5      
    assert len(data["items"]) == 2 
    assert data["limit"] == 2
    assert data["offset"] == 0


def test_get_game_by_id_returns_200():
    created = client.post("/v1/games/", json=SAMPLE_GAME).json()
    response = client.get(f"/v1/games/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["title"] == "The Legend of Zelda"


def test_get_game_unknown_id_returns_404():
    response = client.get("/v1/games/does-not-exist")
    assert response.status_code == 404


def test_search_finds_match():
    client.post("/v1/games/", json=SAMPLE_GAME)
    response = client.get("/v1/games/search?q=zelda")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == "The Legend of Zelda"


def test_search_case_insensitive():
    client.post("/v1/games/", json=SAMPLE_GAME)
    assert client.get("/v1/games/search?q=ZELDA").json()["total"] == 1
    assert client.get("/v1/games/search?q=Zelda").json()["total"] == 1


def test_search_partial_match():
    client.post("/v1/games/", json=SAMPLE_GAME)
    client.post("/v1/games/", json={
        "title": "Zelda: Breath of the Wild",
        "genre": "Adventure",
        "platform": "Nintendo Switch",
    })
    assert client.get("/v1/games/search?q=zelda").json()["total"] == 2


def test_search_no_match_returns_empty():
    client.post("/v1/games/", json=SAMPLE_GAME)
    data = client.get("/v1/games/search?q=mario").json()
    assert data["total"] == 0
    assert data["items"] == []


def test_search_missing_q_returns_422():
    response = client.get("/v1/games/search")
    assert response.status_code == 422