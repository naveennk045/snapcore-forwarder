from sqlalchemy.orm import Session
from .database import SessionLocal

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
