from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

username = 'admin'
password = 'sy7LADkeGFtBxy8'
host = 'shopos-db.cj8uqe0gmqvq.ap-south-1.rds.amazonaws.com'
appdatabase = 'pos'
admindatabase = 'posAdmin'

admin_engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{admindatabase}')

pos_engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{appdatabase}')

AppBase = declarative_base()

AdminBase = declarative_base()