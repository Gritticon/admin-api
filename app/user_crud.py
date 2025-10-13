from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from database.session import  get_admin_db
from database.db_users import User
from schema.s_users import UserBase
from app.verify_user import verify_user
import bcrypt
import secrets

router = APIRouter(prefix="/admin-api/user", tags=["User CRUD Account"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#----------------------------------------------------- Create User API ------------------------------------------------

@router.post('/create_user')
def create_user(
    user_id: int, 
    token: Annotated[str, Depends(oauth2_scheme)], 
    newUser: UserBase, 
    db: Session = Depends(get_admin_db)
    ):

    try: 

        # Validate the requested user
        if not verify_user(user_id, token, db):
            raise HTTPException(status_code=401, detail="Unauthorized user")
        
        # Check if the email already exists
        existing_user = db.query(User).filter(User.email == newUser.email).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists") 
        
        # Hash the password
        hashed_password = bcrypt.hashpw(newUser.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Generate a new token
        new_token = secrets.token_hex(16)

        # generate an incrementing user_id
        last_user = db.query(User).order_by(User.user_id.desc()).first()
        new_user_id = last_user.user_id + 1 if last_user else 1

        # Create a new user instance
        user = User(
            user_id=new_user_id,
            user_name=newUser.user_name,
            email=newUser.email,
            password=hashed_password,
            is_active=1,  
            created_at=datetime.now(),
            created_by=user_id,  
            permissions=newUser.permissions or [],
            token=new_token
        )

        # Add the new user to the session and commit
        db.add(user)
        db.commit()
        db.refresh(user)

        # Return the created user data
        user_data = UserBase(
            user_id=user.user_id,
            user_name=user.user_name,
            email=user.email,
            status=user.is_active,
            permissions=user.permissions or [],
        )     

        return {"message": "User created successfully", "user": user_data.to_dict()}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#----------------------------------------------------- Update User API ------------------------------------------------

@router.put('/update_user')
def update_user(user_id: int, token: Annotated[str, Depends(oauth2_scheme)], updatedUser: UserBase, db: Session = Depends(get_admin_db)):

    try: 

        # Validate the requested user
        if not verify_user(user_id, token, db):
            raise HTTPException(status_code=401, detail="Unauthorized user")
        
        # Find the user to update
        user = db.query(User).filter(User.user_id == updatedUser.user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if the email already exists for another user
        existing_user = db.query(User).filter(User.email == updatedUser.email, User.user_id != updatedUser.user_id).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists for another user")

        # Update user details
        user.user_name = updatedUser.user_name
        user.email = updatedUser.email
        user.permissions = updatedUser.permissions or []

        # Commit the changes to the database
        db.commit()
        db.refresh(user)


        return {"message": "User updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#----------------------------------------------------- Delete User API ------------------------------------------------ 

@router.delete('/delete_user')
def delete_user(user_id: int, user_to_delete: int,token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_admin_db)):

    try: 
        # Validate the requested user
        if not verify_user(user_id, token, db):
            raise HTTPException(status_code=401, detail="Unauthorized user")
        
        # Find the user to delete
        user = db.query(User).filter(User.user_id == user_to_delete).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Delete the user
        user.is_active = 0  
        db.commit()

        return {"message": "User deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#----------------------------------------------------- Get Users API ------------------------------------------------

@router.get('/get_users')
def get_users(user_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_admin_db)):
    
    # Validate the requested user
    if not verify_user(user_id, token, db):
        raise HTTPException(status_code=401, detail="Unauthorized user")
    
    # Retrieve all active users
    users = db.query(User).all()

    if not users:
        raise HTTPException(status_code=404, detail="No active users found")
    
    # Convert users to UserBase schema
    user_list = [UserBase(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        status=user.is_active,
        permissions=user.permissions or [],
        token=user.token
    ).to_dict() for user in users]

    return {"users": user_list}