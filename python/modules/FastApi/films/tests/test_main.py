import pytest
from fastapi.testclient import TestClient
from films.main import app, Film, FilmUpdate, get_films_storage

# Mock storage 
@pytest.fixture
def mock_storage():
    return [
        Film(film_id=1, title="A", description="desc A", release_year=2000),
        Film(film_id=2, title="B", description="desc B", release_year=2001),
    ]

# Override dependency
@pytest.fixture(autouse=True)
def override_dependency(mock_storage):
    app.dependency_overrides[get_films_storage] = lambda: mock_storage
    yield
    app.dependency_overrides.clear()


client = TestClient(app)

def test_get_all_films():
    res = client.get('/films')
    assert res.status_code == 200
    assert len(res.json()) ==  2

def test_get_one_film():
    res = client.get('/films/1')
    assert res.status_code == 200
    assert res.json()['title'] == 'A'

def test_post_film(mock_storage):
    new = {
        'film_id': 100,
        'title': 'movie title',
        'description': 'movie description',
        'release_year': 2025
    }
    res = client.post('/films', json=new)
    assert res.status_code == 200
    assert res.json()['title'] == 'movie title'
    assert len(mock_storage) == 3 

def test_update_film(mock_storage):
    update = {'title': 'Updated A'}
    res = client.put('/films/1', json=update)

    print("STATUS:", res.status_code)
    print("BODY:", res.json())

    assert res.status_code == 200
    assert res.json()['title'] == 'Updated A'

def test_delete_film(mock_storage):
    res = client.delete('/films/1')
    assert res.status_code == 200
    assert res.json()['film_id'] == 1
    assert len(mock_storage) == 1
