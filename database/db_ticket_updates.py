from sqlalchemy import Column, Integer, String, DATETIME, Text
from database.config import AdminBase

class TicketUpdate(AdminBase):
    __tablename__ = 'client_ticket_updates'

    update_id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    attachment = Column(String(50), nullable=True)  # Optional field for attachments
    created_at = Column(DATETIME, nullable=False)
    contact_mode = Column(Integer, nullable=False) # 1 for email, 2 for phone, 3 for chat
    notes = Column(Text, nullable= True)  
