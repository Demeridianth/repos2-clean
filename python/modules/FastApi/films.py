from fastapi import FastAPI, HTTPException
import pandas as pd
from pydantic import BaseModel
from typing import List, Optional


app = FastAPI()

films = pd.read_csv('films_pipe.csv', delimiter='|')

films = films.iloc[:, :4]
films = films.head()
print(films.head())


class Film(BaseModel):
    film_id: int
    title: str
    description: str
    release_year: int

class FilmUpdate(Film):
    film_id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    release_year: Optional[int]


all_films = [
    Film(
        film_id = row['film_id'],
        title = row['title'],
        description = row['description'],
        release_year =  row['release_year']
    )
    for _, row in films.iterrows()
]


# endpoints

@app.get('/films', response_model=List[Film])
def get_films():
    return all_films

@app.get('/films/{film_id}', response_model=Film)
def get_film(film_id: int):
    for film in all_films:
        if film.film_id == film_id:
            return film
    raise HTTPException(status_code=404, detail='Film not found')

@app.post('/films', response_model=Film)
def create_film(film: Film):
    new_film_id = max(film.film_id for film in all_films) + 1
    new_film = Film(
        film_id = new_film_id,
        title = film.title,
        description = film.description,
        release_year = film.release_year
    )
    all_films.append(new_film)
    return new_film

@app.put('/films/{film_id}', response_model=FilmUpdate)
def update_film(film_id: int, updated_film: FilmUpdate):
    for film in all_films:
        if film.film_id == film_id:
            if updated_film.film_id is not None:
                film.film_id = updated_film.film_id
            if updated_film.title is not None:
                film.title = updated_film.title
            if updated_film.description is not None:
                film.description = updated_film.description
            if updated_film.release_year is not None:
                film.release_year = updated_film.release_year
            return film
    raise HTTPException(status_code=404, detail='Film not found')

@app.delete('/films/{film_id}', response_model=Film)
def delete_film(film_id: int):
    for index, film in enumerate(all_films):
        if film.film_id == film_id:
            deleted_film = all_films.pop(index)
        return deleted_film
    raise HTTPException(status_code=404, detail='Film not found')


    
