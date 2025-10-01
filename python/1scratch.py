from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = 'postgresql://postgres:passwor@localhost:5532/my_databe'
engine = create_engine(DATABASE_URL)
SessianLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

# SQLAlchemy model

class DatabaseModel(Base):
    __tablename__ = 'costumers'

    costumer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(String, nullable=False)



    

