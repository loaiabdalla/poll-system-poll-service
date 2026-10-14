"""Database engine, session management, and base models for Poll Service."""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session and ensures closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(max_retries: int = 10, retry_delay: float = 2.0) -> None:
    """Create all database tables with retry logic for container environments."""
    import time
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            print("Poll Service database tables initialized successfully.")
            return
        except Exception as exc:
            if attempt == max_retries:
                raise exc
            print(f"Database not ready yet (attempt {attempt}/{max_retries}), retrying in {retry_delay}s...")
            time.sleep(retry_delay)

