from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


def init_db():
    """Create database tables if they do not exist."""
    Base.metadata.create_all(engine)


def get_db():
    """Yield a new SQLAlchemy session and ensure closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
