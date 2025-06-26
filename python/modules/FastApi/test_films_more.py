from fastapi.testclient import TestClient
from films import app, all_films  # replace with actual module name

client = TestClient(app)

def test_get_all_films():
    response = client.get("/films")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == len(all_films)

def test_get_single_film_success():
    film_id = all_films[0].film_id
    response = client.get(f"/films/{film_id}")
    assert response.status_code == 200
    assert response.json()["film_id"] == film_id

def test_get_single_film_not_found():
    response = client.get("/films/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Film not found"

def test_create_film():
    new_film = {
        "film_id": 999,  # will be overwritten
        "title": "Test Movie",
        "description": "A test film",
        "release_year": 2025
    }
    response = client.post("/films", json=new_film)
    assert response.status_code == 200
    created = response.json()
    assert created["title"] == new_film["title"]
    assert created["description"] == new_film["description"]
    assert created["release_year"] == new_film["release_year"]

def test_update_film():
    film_id = all_films[-1].film_id
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description"
    }
    response = client.put(f"/films/{film_id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Updated Title"
    assert updated["description"] == "Updated Description"

def test_delete_film():
    film_id = all_films[-1].film_id
    response = client.delete(f"/films/{film_id}")
    assert response.status_code == 200
    assert response.json()["film_id"] == film_id

    # Verify deletion
    response_check = client.get(f"/films/{film_id}")
    assert response_check.status_code == 404
