from sqlalchemy import create_engine
<<<<<<< HEAD
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./activities.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
=======
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass

>>>>>>> edcd48e1a2a7c6fcff9913d6467bc578de3d48c8

def get_db():
    db = SessionLocal()
    try:
        yield db
<<<<<<< HEAD
    finally: db.close()
=======
    finally:
        db.close()
>>>>>>> edcd48e1a2a7c6fcff9913d6467bc578de3d48c8
