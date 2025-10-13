from typing import Optional, Dict, List
from pydantic import BaseModel


class ClientBase(BaseModel):
    account_id: int
    business_name: str
    manager: str
    email: str
    phone: int
    street1: str
    street2: Optional[str] = None
    address: str
    state: str
    country_code: int
    postcode: str
    industry_type: int
    subscribed: int = 1  
    active_modules: Optional[List[int]] = None
    onboarded_by: str = 'Direct Sign up'
    onboarded_date: Optional[str] = None
    client_status: Optional[int] = 1 
    device_limit: Optional[int] = 0
    additional_devices: Optional[int] = 0
    additional_modules: Optional[List[int]] = [] 
    package: Optional[int] = 0

    def to_dict(self)->Dict:
        return {
            "account_id": self.account_id,
            "business_name": self.business_name,
            "manager": self.manager,
            "email": self.email,
            "phone": self.phone,
            "street1": self.street1,
            "street2": self.street2,
            "address": self.address,
            "state": self.state,
            "country_code": self.country_code,
            "postcode": self.postcode,
            "industry_type": self.industry_type,
            "subscribed": self.subscribed,
            "active_modules": self.active_modules,
            "onboarded_by": self.onboarded_by,
            "onboarded_date": self.onboarded_date,
            "client_status": self.client_status,
            "device_limit": self.device_limit,
            "additional_devices": self.additional_devices,
            "additional_modules": self.additional_modules,
            "package": self.package
        }