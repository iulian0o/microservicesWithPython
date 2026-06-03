# Module 2 exercise — write your pytest tests here.
#
# Use FastAPI's TestClient to send HTTP requests to your app without
# running a real server. The client is synchronous and works out of the box.
#
# Suggested test cases to get started:
# - POST /v1/users/ with valid data returns 201 and a UserOut body
# - POST /v1/users/ with a duplicate username returns 4xx
# - GET  /v1/users/{id} with a valid ID returns 200 and the correct user
# - GET  /v1/users/{id} with an unknown ID returns 404
# - GET  /v1/users/ returns a UserList with the correct total
#
# Tip: use an in-memory SQLite database in your test fixture so tests
# never touch the real users.db file.
#
# Run tests with:
#   pytest tests/

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_users.db"

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
    """Create all tables before each test, drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

SAMPLE_USER = {
    "username": "iulian",
    "email": "iulian@example.com",
    "password": "secret123",
}


def test_create_user_returns_201():
    response = client.post("/v1/users/", json=SAMPLE_USER)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "iulian"
    assert data["email"] == "iulian@example.com"
    assert "id" in data
    assert "password" not in data          


def test_create_user_duplicate_username_returns_4xx():
    client.post("/v1/users/", json=SAMPLE_USER)
    response = client.post("/v1/users/", json=SAMPLE_USER)
    assert response.status_code >= 400     


def test_get_user_by_id_returns_200():
    created = client.post("/v1/users/", json=SAMPLE_USER).json()
    user_id = created["id"]

    response = client.get(f"/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_get_user_unknown_id_returns_404():
    response = client.get("/v1/users/does-not-exist")
    assert response.status_code == 404


def test_list_users_returns_correct_total():
    assert client.get("/v1/users/").json()["total"] == 0

    client.post("/v1/users/", json=SAMPLE_USER)
    client.post("/v1/users/", json={
        "username": "second_user",
        "email": "second@example.com",
        "password": "pass456",
    })

    data = client.get("/v1/users/").json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_users_pagination():
    for i in range(5):
        client.post("/v1/users/", json={
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "password": "pass",
        })

    response = client.get("/v1/users/?limit=2&offset=0")
    data = response.json()
    assert data["total"] == 5        
    assert len(data["items"]) == 2   
    assert data["limit"] == 2
    assert data["offset"] == 0