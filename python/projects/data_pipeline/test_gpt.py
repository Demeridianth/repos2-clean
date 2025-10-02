import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from python.projects.data_pipeline.main import app, Base, get_db

# ---------------------------
# PostgreSQL test database
# ---------------------------
TEST_DATABASE_URL = "postgresql://postgres:9922296@localhost:5432/dvd_rental_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------
# Pytest fixtures
# ---------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Create a clean schema in the test database.
    Runs once per test session.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Provides a DB session for each test function.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(db_session):
    """
    Provides a TestClient with overridden dependency to use test DB.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

# ---------------------------
# CRUD tests
# ---------------------------

def test_create_film(client):
    response = client.post("/films", json={
        "title": "Inception",
        "description": "Dream heist",
        "release_year": 2010
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Inception"
    assert "film_id" in data

def test_read_films(client):
    # Add a film first
    client.post("/films", json={"title": "Matrix", "description": "Sci-fi", "release_year": 1999})
    response = client.get("/films")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # At least one film exists

def test_read_film_by_id(client):
    create_resp = client.post("/films", json={"title": "Avatar", "description": "Epic", "release_year": 2009})
    film_id = create_resp.json()["film_id"]

    get_resp = client.get(f"/films/{film_id}")
    assert get_resp.status_code == 200
    film = get_resp.json()
    assert film["title"] == "Avatar"

def test_update_film_partial(client):
    create_resp = client.post("/films", json={"title": "Matrix", "description": "Sci-fi", "release_year": 1999})
    film_id = create_resp.json()["film_id"]

    update_resp = client.put(f"/films/{film_id}", json={"release_year": 2000})
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["release_year"] == 2000
    assert updated["title"] == "Matrix"
    assert updated["description"] == "Sci-fi"

def test_delete_film(client):
    create_resp = client.post("/films", json={"title": "DeleteMe", "description": "Temp", "release_year": 2022})
    film_id = create_resp.json()["film_id"]

    delete_resp = client.delete(f"/films/{film_id}")
    assert delete_resp.status_code == 200

    get_resp = client.get(f"/films/{film_id}")
    assert get_resp.status_code == 404

# ---------------------------
# CSV injection test
# ---------------------------

def test_inject_csv(client):
    response = client.post("/films/inject_csv")
    assert response.status_code == 200
    films = response.json()
    assert isinstance(films, list)
    assert len(films) <= 5  # Only first 5 rows from CSV are injected
    for film in films:
        assert "title" in film
        assert "film_id" in film
