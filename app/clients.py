from datetime import datetime, timezone, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_app_db, get_admin_db
from schema.s_client_update import ClientUpdate
from database.db_customer import Client, ClientMain, ClientSettings, ClientSubscription
from database.db_packages import Package
from schema.s_client import ClientBase 
from schema.s_client_list_base import ClientListBase
from core.security import get_user_id, get_bearer_token, verify_user
from database.db_updates import TrackUpdate
from utils.send_updates import send_device1_update


router = APIRouter(prefix="/admin-api/customers", tags=[" Account"])

#------------------------------------- Get Client Search List API ------------------------------------------------

@router.get('/get_all_clients')
async def get_all_clients(
    user_id: Annotated[int, Depends(get_user_id)],
    token: Annotated[str, Depends(get_bearer_token)],
    appDb: Session = Depends(get_app_db),
    adminDb: Session = Depends(get_admin_db)
    ):

    # Validate the user
    if not verify_user(user_id, token, adminDb):
        raise HTTPException(status_code=401, detail="Unauthorized user")

    # Fetch all clients
    clients = appDb.query(Client).all()

    # Fetch only account_id, email, and account_status from ClientMain
    clientMainRows = appDb.query(
        ClientMain.account_id,
        ClientMain.business_email,
        ClientMain.account_status
    ).all()

    # Build a dictionary for quick lookup: {account_id: (email, account_status)}
    clientMainData = {row.account_id: (row.business_email, row.account_status) for row in clientMainRows}

    # Fetch subscriptions
    clientSubscriptionData = appDb.query(ClientSubscription).all()

    def get_subscription_data(account_id: int):
        for subscription in clientSubscriptionData:
            if subscription.account_id == account_id:
                return subscription
        return None

    clients_list = []

    for client in clients:
        email, account_status = clientMainData.get(client.account_id, ("", None))
        subscription = get_subscription_data(client.account_id)

        client_data = ClientListBase(
            account_id=client.account_id,
            business_name=client.business_name,
            phone=client.phone,
            email=email,
            subscribed=subscription.subscribed if subscription else 0,
            package=subscription.package_id if subscription else 0,
            account_status=account_status,
            onboarding=str(client.onboarded_date.strftime("%Y-%m-%dT%H:%M:%S.%f"))
            if client.onboarded_date else None,
        )
        clients_list.append(client_data)

    # Return the list of clients
    return {"clients": [client.to_dict() for client in clients_list]}

#------------------------------------- Get specific client API ------------------------------------------------

@router.get('/get_specific_client')
async def get_specific_client(
    user_id: Annotated[int, Depends(get_user_id)],
    token: Annotated[str, Depends(get_bearer_token)],
    account_id: int,
    appDb: Session = Depends(get_app_db),
    adminDb: Session = Depends(get_admin_db)
    ):

    # Validate the user
    if not verify_user(user_id, token, adminDb):
        raise HTTPException(status_code=401, detail="Unauthorized user")

    # Fetch the specific client from the database
    client = appDb.query(Client).filter(Client.account_id == account_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client_main = appDb.query(ClientMain).filter(ClientMain.account_id == account_id).first()

    client_settings = appDb.query(ClientSettings).filter(ClientSettings.account_id == account_id).first()

    client_subscription = appDb.query(ClientSubscription).filter(ClientSubscription.account_id == account_id).first()

    client_data = ClientBase(
        account_id=client.account_id,
        business_name=client.business_name,
        manager=client.manager,
        email=client_main.business_email,
        phone=client.phone,
        street1=client.street1,
        street2=client.street2,
        address=client.address,
        state=client.state,
        country_code=client.country_code,
        postcode=client.postcode,
        industry_type=client.industry_type,
        subscribed=client_subscription.subscribed,
        active_modules=client_subscription.active_modules or [],
        onboarded_by=client.onboarded_by,
        onboarded_date= str(client.onboarded_date.strftime("%Y-%m-%dT%H:%M:%S.%f")) if client.onboarded_date else None,
        client_status= client_main.account_status,
        device_limit=client_subscription.device_limit if client_subscription else 0,
        additional_devices=client_subscription.additional_devices if client_subscription else 0,
        additional_modules=client_subscription.additional_modules if client_subscription else [],
        package=client_subscription.package_id if client_subscription else 0
    )

    # Return the client data
    return {"client": client_data.to_dict()}

#------------------------------------- Update Client Subscription API ------------------------------------------------

@router.post('/update_client_subscription')
async def update_client_subscription(
    user_id: Annotated[int, Depends(get_user_id)],
    token: Annotated[str, Depends(get_bearer_token)],
    request: ClientUpdate,
    appDb: Session = Depends(get_app_db),
    adminDb: Session = Depends(get_admin_db)
    ):
    try:
        # Validate the user
        if not verify_user(user_id, token, adminDb):
            raise HTTPException(status_code=401, detail="Unauthorized user")

        # Fetch the client from the database
        client = appDb.query(Client).filter(Client.account_id == request.account_id).first()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Initialize package variables
        package = None
        package_device_limit = 0
        package_active_modules = []
        package_id = request.package_id or 0
        
        # If package_id is provided and not 0, fetch the package
        if package_id > 0:
            package = adminDb.query(Package).filter(
                Package.id == package_id,
                Package.status == 1  # Only active packages
            ).first()
            
            if not package:
                raise HTTPException(status_code=404, detail=f"Package with ID {package_id} not found or inactive")
            
            package_device_limit = package.device_limit or 0
            package_active_modules = package.active_modules or []
        
        # Calculate final values: package base + additional values
        additional_devices = request.additional_devices or 0
        additional_modules = request.additional_modules or []
        
        # Final device limit = package device limit + additional devices
        # If no package (package_id = 0), final = additional_devices only
        final_device_limit = package_device_limit + additional_devices
        
        # Final active modules = package modules + additional modules (union, remove duplicates)
        # If no package (package_id = 0), final = additional_modules only
        final_active_modules = list(set(package_active_modules + additional_modules))
        
        # Fetch or create ClientSubscription record
        client_subscription = appDb.query(ClientSubscription).filter(
            ClientSubscription.account_id == request.account_id
        ).first()
        
        if not client_subscription:
            # Create new ClientSubscription record
            client_subscription = ClientSubscription(
                account_id=request.account_id,
                subscribed=request.subscribed or 1,
                package_id=package_id,
                additional_devices=additional_devices,
                additional_modules=additional_modules,
                active_modules=final_active_modules,
                device_limit=final_device_limit
            )
            appDb.add(client_subscription)
        else:
            # Update existing ClientSubscription record
            # Only update subscribed if explicitly provided, otherwise keep existing value
            if request.subscribed is not None:
                client_subscription.subscribed = request.subscribed
            client_subscription.package_id = package_id
            client_subscription.additional_devices = additional_devices
            client_subscription.additional_modules = additional_modules
            client_subscription.active_modules = final_active_modules
            client_subscription.device_limit = final_device_limit

        # Clean up old updates (older than 45 days)
        old_updates = adminDb.query(TrackUpdate).filter(
            TrackUpdate.updated_at < datetime.now(timezone.utc) - timedelta(days=45)
        ).all()
        
        if old_updates:
            for update in old_updates:
                adminDb.delete(update)
            adminDb.commit()

        # Prepare update data for notification
        update_data = {
            "account_id": request.account_id,
            "subscribed": client_subscription.subscribed,
            "active_modules": final_active_modules,
            "device_limit": final_device_limit,
            "package_id": package_id,
            "additional_devices": additional_devices,
            "additional_modules": additional_modules
        }

        # Send update notification to client devices
        await send_device1_update(request.account_id, 60, update_data)

        # Create a track update entry
        track_update = TrackUpdate(
            update_data=update_data,
            updated_at=datetime.now(timezone.utc),
            updated_by=user_id,
            account_id=request.account_id
        )

        # Add the track update to the session
        adminDb.add(track_update)

        # Commit all changes to the database
        appDb.commit()
        adminDb.commit()

        # Return success response with calculated values
        return {
            "message": "Client subscription updated successfully",
            "data": {
                "account_id": request.account_id,
                "package_id": package_id,
                "package_name": package.name if package else None,
                "subscribed": client_subscription.subscribed,
                "final_device_limit": final_device_limit,
                "final_active_modules": final_active_modules,
                "package_device_limit": package_device_limit,
                "package_active_modules": package_active_modules,
                "additional_devices": additional_devices,
                "additional_modules": additional_modules
            }
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions (like 401, 404)
        raise
    except Exception as e:
        # Rollback on error
        appDb.rollback()
        adminDb.rollback()
        # Handle exceptions and return an error message
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")