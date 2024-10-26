from fastapi_users import FastAPIUsers
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.authentication import JWTStrategy
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import uuid

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


class User(BaseModel):
    id: uuid.UUID
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False


async def get_user_db(session: AsyncSession = Depends(SessionLocal)):
    yield SQLAlchemyUserDatabase(User, session)


SECRET = "SECRET"


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = JWTStrategy(secret=SECRET, lifetime_seconds=3600)


app = FastAPI()

fastapi_users = FastAPIUsers(get_user_db, [auth_backend])
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_register_router(), prefix="/auth", tags=["auth"])
