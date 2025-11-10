"""
Database Session Management
SQLAlchemy session factories and dependency injection.
"""
from sqlalchemy.orm import sessionmaker
from core.database import pos_engine, admin_engine

AppSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pos_engine)

AdminSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)

def get_app_db():
    """Dependency for application database session."""
    db = AppSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_admin_db():
    """Dependency for admin database session."""
    db = AdminSessionLocal()
    try:
        yield db
    finally:
        db.close()