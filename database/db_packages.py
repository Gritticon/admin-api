from sqlalchemy import  Column, Integer, String, DATETIME, Text, JSON, Float
from core.database import AdminBase

class Package(AdminBase):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    active_modules = Column(JSON, nullable=True)
    device_limit = Column(Integer, nullable=True)
    status = Column(Integer, nullable=False, default=1)  # 1 for active, 0 for inactive
    notes = Column(Text, nullable=True)
    price = Column(Float, nullable=False, default=0)  # in cents
    created_at = Column(DATETIME, nullable=False)
    created_by = Column(Integer, nullable=False)  
