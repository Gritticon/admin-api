from typing import Optional
from pydantic import BaseModel

class ClientUpdate(BaseModel):
    user_id: int
    account_id: int
    subscribed: Optional[int] = 1
    active_modules: Optional[list[int]] = None
    device_limit: Optional[int] = 0

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "account_id": self.account_id,
            "subscribed": self.subscribed,
            "active_modules": self.active_modules or [],
            "device_limit": self.device_limit
        }