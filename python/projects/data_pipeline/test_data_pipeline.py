import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_pipeline import app, Base, get_db


# PostgreSQL test database
TEST_DATABASE_URL = "postgresql://postgres:9922296@localhost:5432/dvd_rental_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pytest fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='function')
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope='function')
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

# CRUD tests

def test_create_film(client):
    response = client.post('/films', json = {
        "title": "Inception",
        "description": "Dream Heist",
        "release_year": 2010 
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Inception"
    assert "film_id" in data