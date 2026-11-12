"""SQLite + SQLAlchemy. Lab project: runs on any laptop with no server,
no Docker and no cloud account. The data model is the same shape as a
GRC register, so it maps 1:1 to Archer, ServiceNow IRM or OneTrust."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./azure_native_governance.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
