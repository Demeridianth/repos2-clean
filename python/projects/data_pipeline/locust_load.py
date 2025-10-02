from locust import HttpUser, task, between
import random

class FilmUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    @task(2)  # Weight 2 → more frequent
    def get_films(self):
        self.client.get("/films")

    @task(1)
    def get_random_film(self):
        # Choose random film_id between 1 and 10 (adjust if you have more)
        film_id = random.randint(1, 10)
        self.client.get(f"/films/{film_id}")

    @task(1)
    def create_film(self):
        new_film = {
            "title": f"Test Film {random.randint(1000, 9999)}",
            "description": "Load test",
            "release_year": 2025
        }
        self.client.post("/films", json=new_film)

    @task(1)
    def update_film(self):
        # Update a random film
        film_id = random.randint(1, 10)
        updated = {"description": "Updated during load test"}
        self.client.put(f"/films/{film_id}", json=updated)
