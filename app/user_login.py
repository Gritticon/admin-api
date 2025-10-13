from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from database.session import get_admin_db
from database.db_users import User
from schema.s_users import UserBase
import bcrypt

router = APIRouter(prefix="/login", tags=["Admin User Account"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post('/admin-api/admin_login')
def login_admin(email:str, password:str, db: Session = Depends(get_admin_db)):

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    user = db.query(User).filter(User.email == email).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    
    elif bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        user_data = UserBase(
            user_id=user.user_id,
            user_name=user.user_name,
            email=user.email,
            status=user.is_active,
            permissions=user.permissions or [],
            token=user.token
        )
        return {"message": "Login successful", "user": user_data.to_dict()}
    
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

