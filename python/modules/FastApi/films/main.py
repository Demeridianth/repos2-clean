from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

import pandas as pd

app = FastAPI()

# Load from CSV only for actual app startup
films_df = pd.read_csv('films_pipe.csv', delimiter='|').iloc[:, :4].head()


class Film(BaseModel):
    film_id: int
    title: str
    description: str
    release_year: int


class FilmUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None

all_films = [
        Film(
            film_id=row["film_id"],
            title=row["title"],
            description=row["description"],
            release_year=row["release_year"],
        )
        for _, row in films_df.iterrows()
    ]
# Dependency: get in-memory "database"
def get_films_storage():
    return all_films

@app.get("/films", response_model=List[Film])
def get_films(films=Depends(get_films_storage)):
    return films


@app.get("/films/{film_id}", response_model=Film)
def get_film(film_id: int, films=Depends(get_films_storage)):
    for film in films:
        if film.film_id == film_id:
            return film
    raise HTTPException(status_code=404, detail="Film not found")


@app.post("/films", response_model=Film)
def create_film(film: Film, films=Depends(get_films_storage)):
    new_film_id = max(f.film_id for f in films) + 1
    new_film = Film(
        film_id=new_film_id,
        title=film.title,
        description=film.description,
        release_year=film.release_year,
    )
    films.append(new_film)
    return new_film


@app.put("/films/{film_id}", response_model=Film)
def update_film(film_id: int, updated_film: FilmUpdate, films=Depends(get_films_storage)):
    print("Received update:", updated_film)
    for film in films:
        if film.film_id == film_id:
            if updated_film.title is not None:
                film.title = updated_film.title
            if updated_film.description is not None:
                film.description = updated_film.description
            if updated_film.release_year is not None:
                film.release_year = updated_film.release_year
            return film
    raise HTTPException(status_code=404, detail="Film not found")


@app.delete("/films/{film_id}", response_model=Film)
def delete_film(film_id: int, films=Depends(get_films_storage)):
    for i, film in enumerate(films):
        if film.film_id == film_id:
            return films.pop(i)
    raise HTTPException(status_code=404, detail="Film not found")
