from sqlalchemy import Column,  Integer, String, BigInteger, Text, DateTime, JSON, Boolean, Float
from core.database import AppBase 

class Client(AppBase):
    __tablename__ = "BusinessDetails"
    __table_args__ = {'extend_existing': True}

    account_id = Column(Integer, primary_key= True)
    business_name = Column(String(100))
    business_logo = Column(Text)
    manager = Column(String(50))
    phone = Column(BigInteger)
    street1 = Column(String(100))
    street2 = Column(String(100), default= '')
    address = Column(String(150))
    state = Column(String(150))
    country_code = Column(Integer)
    postcode = Column(String(50))
    industry_type = Column(Integer)
    onboarded_by = Column(String(75))
    onboarded_date = Column(DateTime)


class ClientMain(AppBase):
    __tablename__ = "Customers"
    __table_args__ = {'extend_existing': True}

    account_id = Column(Integer, primary_key=True)
    account_status = Column(Integer, default= 1)
    business_email = Column(String(100), unique= True)
    password = Column(Text)
    account_token = Column(String(255))
    web_token = Column(String(255))

class ClientSettings(AppBase):
    __tablename__ = "BusinessSettings"
    __table_args__ = {'extend_existing': True}

    account_id = Column(Integer, primary_key= True)
    inventory = Column(Boolean, default= False)
    web_settings = Column(Boolean, default= False)
    unit_pricing = Column(Boolean, default= False)
    use_barcode = Column(Boolean, default= False)
    admin_pin = Column(Integer, default=0)
    admin_pin_modules = Column(JSON)



class ClientSubscription(AppBase):
    __tablename__ = "BusinessSubscription"
    account_id = Column(Integer, primary_key= True)
    subscribed = Column(Integer, default=1)
    active_modules = Column(JSON, default=[])
    device_limit = Column(Integer, default= 2)
    package_id = Column(Integer, default= 0)
    additional_devices = Column(Integer, default = 0)
    chargeAmount = Column(Float, default= 0.00)
    additional_modules = Column(JSON, default=[])
