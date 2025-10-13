from pydantic import BaseModel
from typing import Optional, Dict

class TicketUpdateSchema(BaseModel):
    ticket_id: int
    description: str  # Update description
    created_at: str  # Should be in ISO format
    updated_by: int  # User ID of the person making the update
    attachment: Optional[str] = None  # Optional field for attachments
    contact_mode: int  # 1 for email, 2 for phone, 3 for chat
    notes: Optional[str] = None  # Optional field for additional notes

    def to_dict(self) -> Dict:
        return {
            "ticket_id": self.ticket_id,
            "description": self.description,
            "created_at": self.created_at,
            "updated_by": self.updated_by,
            "attachment": self.attachment,
            "contact_mode": self.contact_mode,
            "notes": self.notes
        }