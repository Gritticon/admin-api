from pydantic import BaseModel
from typing import Dict, List, Optional

class UserBase(BaseModel):
    user_id: int
    user_name: str
    email: str
    status: int
    password: Optional[str] = None
    permissions : List[int] = []
    token: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "email": self.email,
            "status": self.status,
            "permissions": self.permissions,
            "token": self.token
        }