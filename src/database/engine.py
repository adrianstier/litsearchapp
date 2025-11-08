"""Database engine and session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from pathlib import Path

from src.utils.config import Config
from .models import Base

# Create database directory
db_dir = Config.BASE_DIR / "database"
db_dir.mkdir(parents=True, exist_ok=True)

# Database URL
DATABASE_URL = f"sqlite:///{db_dir / 'papers.db'}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=Config.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized at {db_dir / 'papers.db'}")


@contextmanager
def get_db() -> Session:
    """
    Get database session context manager

    Usage:
        with get_db() as db:
            db.query(Paper).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get database session (for FastAPI dependency injection)

    Usage:
        def endpoint(db: Session = Depends(get_db_session)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()