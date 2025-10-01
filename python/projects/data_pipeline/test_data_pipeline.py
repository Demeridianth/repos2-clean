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

# drops if anything in test table, creates a new test table and then drops it again
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# creates MOCK test session
@pytest.fixture(scope='function')
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# replaces REAL one in the program with the MOCK one
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

def test_read_films(client):
    client.post('/films', json={'tile': "Movie1", 'description': 'its a movie', 'release_year': 1999})
    response = client.get('/films')
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_read_film_by_id(client):
    create_response = client.post('/films', json={'tile': "Movie1", 'description': 'its a movie', 'release_year': 1999})
    film_id = create_response.json()['film_id']

    get_response = client.get(f'/films/{film_id}')
    assert get_response.status_code == 200
    film = get_response.json()
    assert film['title'] == 'Movie1'

def test_update_film(client):
    create_response = client.post('/films', json={'title': "Movie1", 'description': 'its a movie', 'release_year': 1999})
    film_id = create_response.json()['film_id']

    update_response = client.put(f'films/{film_id}', json={'release_year': 2000})
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['release_year'] == 2000
    assert updated['title'] == 'Movie1'

def test_delete_film(client):
    create_response = client.post('/films', json={'tile': "Movie1", 'description': 'its a movie', 'release_year': 1999})
    film_id = create_response.json()['film_id']

    deleted_response = client.delete('/film/{film_id}')
    assert deleted_response.status_code == 200
    get_deleted_response = client.get('/films/{film_id}')
    assert get_deleted_response.status_code == 404

