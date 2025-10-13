from sqlalchemy import  Column, Integer, String, DATETIME, Text
from database.config import AdminBase

class Ticket(AdminBase):
    __tablename__ = 'client_tickets'

    ticket_id = Column(Integer, primary_key=True)
    account_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    subject = Column(String(225), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Integer, nullable=False, default=1) # 1 for open, 2 for under review, 3 for closed
    priority = Column(Integer, nullable=False, default=1) # 1 for low, 2 for medium, 3 for high
    created_at = Column(DATETIME, nullable=False)
    contact_mode = Column(Integer, nullable=False) # 1 for email, 2 for phone, 3 for chat
    clinet_name = Column(String(100), nullable=False)
    client_phone = Column(String(50), nullable=False)
    clinet_email = Column(String(100), nullable=False)
    attachment = Column(String(50), nullable=True) 
    notes = Column(Text, nullable=True)  
