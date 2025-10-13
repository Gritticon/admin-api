from sqlalchemy.orm import sessionmaker
from database.config import pos_engine, admin_engine

AppSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pos_engine)

AdminSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)

def get_app_db():
    db = AppSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_admin_db():
    db = AdminSessionLocal()
    try:
        yield db
    finally:
        db.close()