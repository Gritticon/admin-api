from sqlalchemy import Column,  Integer, String, DateTime, JSON
from core.database import AdminBase

class TrackUpdate(AdminBase):
    __tablename__ = "TrackUpdates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    update_data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    updated_by = Column(String(100), nullable=False) 
    account_id = Column(Integer, nullable=False)  