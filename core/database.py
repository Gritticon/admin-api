"""
Database Configuration
SQLAlchemy engine and declarative base setup.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from core.config import settings

# Create database engines using settings
pos_engine = create_engine(settings.app_database_url)
admin_engine = create_engine(settings.admin_database_url)

# Declarative bases for models
AppBase = declarative_base()
AdminBase = declarative_base()

