from fastapi import FastAPI, HTTPException
import pandas as pd
from pydantic import BaseModel
from typing import List, Optional, Dict

# faster O(1)

app = FastAPI()

films = pd.read_csv('films_pipe.csv', delimiter='|')
films = films.iloc[:, :4].head(5)

class Film(BaseModel):
    film_id: int
    title: str
    description: str
    release_year: int

class FilmOptional(BaseModel):  # Inherit from BaseModel, not Film
    film_id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    release_year: Optional[int]

# Convert DataFrame to dict[int, Film]
film_dict: Dict[int, Film] = {
    int(row['film_id']): Film(
        film_id=int(row['film_id']),
        title=row['title'],
        description=row['description'],
        release_year=int(row['release_year'])
    )
    for _, row in films.iterrows()
}

@app.get('/', response_model=List[Film])
def get_all_films():
    return list(film_dict.values())

@app.get('/films/{film_id}', response_model=Film)
def get_film_by_id(film_id: int):
    if film_id not in film_dict:
        raise HTTPException(status_code=404, detail='Record not found')
    return film_dict[film_id]

@app.post('/', response_model=Film)
def create_film(new_film: Film):
    new_film_id = max(film_dict.keys(), default=0) + 1
    new_film.film_id = new_film_id
    film_dict[new_film_id] = new_film
    return new_film

@app.put('/film/{film_id}', response_model=Film)
def edit_film(film_id: int, updated_film: FilmOptional):
    if film_id not in film_dict:
        raise HTTPException(status_code=404, detail='Record not found')

    film = film_dict[film_id]

    updated_data = film.dict()
    if updated_film.film_id is not None:
        updated_data['film_id'] = updated_film.film_id
    if updated_film.title is not None:
        updated_data['title'] = updated_film.title
    if updated_film.description is not None:
        updated_data['description'] = updated_film.description
    if updated_film.release_year is not None:
        updated_data['release_year'] = updated_film.release_year

    # Update or change the film_id key if needed
    if updated_film.film_id is not None and updated_film.film_id != film_id:
        film_dict.pop(film_id)
        film_id = updated_film.film_id  # new key

    film_dict[film_id] = Film(**updated_data)
    return film_dict[film_id]

@app.delete('/film/{film_id}', response_model=Film)
def delete_film(film_id: int):
    if film_id not in film_dict:
        raise HTTPException(status_code=404, detail='Record not found')
    return film_dict.pop(film_id)
