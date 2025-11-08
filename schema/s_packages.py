from typing import Optional, List
from pydantic import BaseModel

class PackageBase(BaseModel):
    id: int
    name: str
    active_modules: Optional[List] = []
    device_limit: Optional[int] = None
    status: int  # 1 for active, 0 for inactive
    notes: Optional[str] = None
    price: float  # in cents
    created_at: Optional[str] = None  # ISO format datetime string
    created_by: Optional[int] = None