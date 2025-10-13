from pydantic import BaseModel
from typing import Dict, List, Optional

class TransactionBase(BaseModel):
    transaction_id: int
    service_provider: str
    user_id: int
    amount: int
    email: str
    phone_number: str
    transaction_category: int
    payment_method: int
    transaction_date: str 
    recorded_date: str 
    comments: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "service_provider": self.service_provider,
            "user_id": self.user_id,
            "amount": self.amount,
            "email": self.email,
            "phone_number": self.phone_number,
            "transaction_category": self.transaction_category,
            "payment_method": self.payment_method,
            "transaction_date": self.transaction_date,
            "recorded_date": self.recorded_date,
            "comments": self.comments
        }