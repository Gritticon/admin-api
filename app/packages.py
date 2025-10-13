from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.verify_user import verify_user
from database.session import get_admin_db
from database.db_packages import Package
from schema.s_packages import PackageBase
from typing import Annotated
from datetime import datetime


router = APIRouter(prefix="/packages", tags=["Package CRUD Operations"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#----------------------------------------------------- Create Package API ------------------------------------------------

@router.post('/admin-api/create_package')
def create_package(
    user_id: int, 
    token: Annotated[str, Depends(oauth2_scheme)], 
    package_data: PackageBase, 
    adminDb: Session = Depends(get_admin_db)
    ):

    # Validate the requested user
    if not verify_user(user_id, token, adminDb):
        raise HTTPException(status_code=401, detail="Unauthorized user")
    
    try:
        # Get the highest current package ID
        max_id = adminDb.query(Package).order_by(Package.id.desc()).first()

        # Create a new package instance
        new_package = Package(
            id = (max_id.id + 1) if max_id else 1,
            name=package_data.name,
            active_modules=package_data.active_modules,
            device_limit=package_data.device_limit,
            status=package_data.status,
            notes=package_data.notes or None,
            price=package_data.price,
            created_at=datetime.now(),
            created_by=user_id
        )
        
        # Add and commit the new package to the database
        adminDb.add(new_package)
        adminDb.commit()
        adminDb.refresh(new_package)
        
        return {"message": "Package created successfully", "package_id": new_package.id}
    
    except Exception as e:
        adminDb.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
#----------------------------------------------------- Delete Package API ------------------------------------------------

@router.delete('/admin-api/delete_package')
def delete_package(
    user_id: int, 
    token: Annotated[str, Depends(oauth2_scheme)], 
    package_id: int, 
    adminDb: Session = Depends(get_admin_db)
    ):

    # Validate the requested user
    if not verify_user(user_id, token, adminDb):
        raise HTTPException(status_code=401, detail="Unauthorized user")
    
    try:
        # Fetch the package to be deleted
        package = adminDb.query(Package).filter(Package.id == package_id).first()
        
        if not package:
            raise HTTPException(status_code=404, detail="Package not found")
        
        # Delete the package
        package.status = 0  
        adminDb.commit()
        
        return {"message": "Package deleted successfully"}
    
    except Exception as e:
        adminDb.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

#----------------------------------------------------- Get Packages API ------------------------------------------------

@router.get('/admin-api/get_packages')
def get_packages(
    user_id: int, 
    token: Annotated[str, Depends(oauth2_scheme)], 
    adminDb: Session = Depends(get_admin_db)
    ):

    # Validate the requested user
    if not verify_user(user_id, token, adminDb):
        raise HTTPException(status_code=401, detail="Unauthorized user")
    
    # Fetch all active packages
    packages = adminDb.query(Package).filter(Package.status == 1).all()

    output = []

    for pkg in packages:
        pkg_dict = PackageBase(
            id=pkg.id,
            name=pkg.name,
            active_modules=pkg.active_modules or [],
            device_limit=pkg.device_limit,
            status=pkg.status,
            notes=pkg.notes,
            price=pkg.price,
            created_at=pkg.created_at.isoformat(),
            created_by=pkg.created_by
        )
        output.append(pkg_dict)

    return {"packages": output}