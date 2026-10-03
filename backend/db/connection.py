import os

import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

dotenv.load_dotenv()

database_url = os.getenv("sql_connection", "sqlite:///./voice_agent.db")

engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False}
    if database_url.startswith("sqlite")
    else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI/generator style dependency. Yields a session and closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Importing backend.models registers every model
    on Base.metadata, so they must be imported before create_all runs."""
    import backend.models  # noqa: F401  (ensures models are registered)

    Base.metadata.create_all(bind=engine)
