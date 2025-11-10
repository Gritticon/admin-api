from typing import Optional, List
from pydantic import BaseModel

class ClientUpdate(BaseModel):
    account_id: int
    package_id: Optional[int] = None  # Package template ID (0 or None means no package)
    subscribed: Optional[int] = 1  # Subscription status (1 = active, 0 = inactive)
    additional_devices: Optional[int] = 0  # Additional devices on top of package device_limit
    additional_modules: Optional[List[int]] = []  # Additional modules on top of package active_modules

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "package_id": self.package_id or 0,
            "subscribed": self.subscribed,
            "additional_devices": self.additional_devices or 0,
            "additional_modules": self.additional_modules or []
        }