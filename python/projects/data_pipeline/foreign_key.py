from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class FilmDB(Base):
    __tablename__ = "films"

    film_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    release_year = Column(Integer)

    # Optional: relationship to Actor table (many-to-many via film_actor)
    actors = relationship("FilmActorDB", back_populates="film")

class ActorDB(Base):
    __tablename__ = "actors"

    actor_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    films = relationship("FilmActorDB", back_populates="actor")

class FilmActorDB(Base):
    __tablename__ = "film_actor"

    film_id = Column(Integer, ForeignKey("films.film_id"), primary_key=True)
    actor_id = Column(Integer, ForeignKey("actors.actor_id"), primary_key=True)

    film = relationship("FilmDB", back_populates="actors")
    actor = relationship("ActorDB", back_populates="films")




class FilmDB(Base):
    __tablename__ = "films"
    film_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    release_year = Column(Integer)

class ActorDB(Base):
    __tablename__ = "actors"
    actor_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

class FilmActorDB(Base):
    __tablename__ = "film_actor"
    film_id = Column(Integer, ForeignKey("films.film_id"), primary_key=True)
    actor_id = Column(Integer, ForeignKey("actors.actor_id"), primary_key=True)