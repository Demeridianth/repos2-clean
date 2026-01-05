from fastapi import FastAPI, HTTPException, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped, mapped_column, configure_mappers, lazyload, selectinload
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from food_app.api import restaurants, orders
from food_app.database import engine, AsyncSessionLocal 


# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(
    title="Food Service API",
    description="Async API for food service",
    version="1.0.0"
)


# ======================
# CORS for frontend dev
# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # In production, set your frontend URL, like   allow_origins=["https://myfrontend.com"]
    allow_methods=["*"],    # Which HTTP methods are allowed (GET, POST, etc.)
    allow_headers=["*"],    # Which headers are allowed (like Authorization)
    allow_credentials=True,  # Allow cookies or authentication headers
)





# ---------------------------
# Endpoint routers              # MUST BE AT THE END OF MAIN
# ---------------------------
app.include_router(restaurants.router)
app.include_router(orders.router)