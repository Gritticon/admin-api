from typing import Dict, Optional
from pydantic import BaseModel

class ClientListBase(BaseModel):
    account_id: int
    business_name: str
    phone: int
    email: str
    subscribed: int
    package: int
    onboarding: Optional[str] = None 
    account_status: int

    def to_dict(self) -> Dict:
        return {
            "account_id": self.account_id,
            "business_name": self.business_name,
            "phone": self.phone,
            "email": self.email,
            "subscribed": self.subscribed,
            "package": self.package,
            "onboarding": self.onboarding,
            "account_status": self.account_status
        }