from sqlalchemy import  Column, Integer, String, DATETIME, Text
from core.database import AdminBase

class Transaction(AdminBase):
    __abstract__ = True

    transaction_id = Column(Integer, primary_key=True)
    service_provider = Column(String(50), nullable=False)
    user_id = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    email = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False)
    transaction_category = Column(Integer, nullable=False)
    payment_method = Column(Integer, nullable=False)
    transaction_date = Column(DATETIME, nullable=False)
    recorded_date = Column(DATETIME, nullable=False)
    comments = Column(Text, nullable=True)