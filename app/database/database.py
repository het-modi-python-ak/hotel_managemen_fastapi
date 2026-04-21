from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine,AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession

load_dotenv()



DATABASE_URL = os.getenv("DATABASE_URL")


# engine = create_engine(
#     DATABASE_URL
# )

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Useful for debugging SQL queries
)


# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )



AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
   


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

Base = declarative_base()