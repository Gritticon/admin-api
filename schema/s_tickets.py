from pydantic import BaseModel
from typing import Optional, Dict

class TicketSchema(BaseModel):
    ticket_id: int
    account_id: int
    user_id: int
    subject: str
    description: str
    status: int = 1  # Default to open
    priority: int = 1  # Default to low
    created_at: str  # Should be in ISO format
    contact_mode: int  # 1 for email, 2 for phone, 3 for chat
    client_name: str
    client_phone: Optional[str] = None  # Optional field
    client_email: Optional[str] = None  # Optional field
    attachment: Optional[str] = None 
    notes: Optional[str] = None # Optional field for attachments

    def to_dict(self) -> Dict:
        return {
            "ticket_id": self.ticket_id,
            "account_id": self.account_id,
            "user_id": self.user_id,
            "subject": self.subject,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at,
            "contact_mode": self.contact_mode,
            "client_name": self.client_name,
            "client_phone": self.client_phone,
            "client_email": self.client_email,
            "attachment": self.attachment,
            "notes": self.notes
        } 

    