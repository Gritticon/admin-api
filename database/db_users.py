from sqlalchemy import  Column, Integer, String, JSON, DATETIME
from database.config import AdminBase

class User(AdminBase):
    __tablename__ = "AdminUsers"

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)  
    created_at = Column(DATETIME, nullable=False)
    created_by = Column(Integer, nullable=False)
    permissions = Column(JSON, nullable=True)
    token = Column(String(255), nullable=False)
