from datetime import datetime, timezone, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from database.session import get_app_db, get_admin_db
from schema.s_client_update import ClientUpdate
from database.db_customer import Client, ClientMain, ClientSettings, ClientSubscription
from schema.s_client import ClientBase 
from schema.s_client_list_base import ClientListBase
from app.verify_user import verify_user
from database.db_updates import TrackUpdate
from send_updates import send_device1_update


router = APIRouter(prefix="/customers", tags=[" Account"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#------------------------------------- Get Client Search List API ------------------------------------------------

@router.get('/admin-api/get_all_clients')
def get_all_clients(
    user_id: int, 
    token: Annotated[str, Depends(oauth2_scheme)], 
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

@router.get('/admin-api/get_specific_client')
def get_specific_client(
    user_id: int, 
    account_id: int, 
    token: Annotated[str, Depends(oauth2_scheme)],  
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

@router.post('/admin-api/update_client_subscription')
async def update_client_subscription(
    request: ClientUpdate, 
    token: Annotated[str, Depends(oauth2_scheme)],  
    appDb: Session = Depends(get_app_db),
    adminDb: Session = Depends(get_admin_db)
    ):
    try:
        # Validate the user
        if not verify_user(request.user_id, token, adminDb):
            raise HTTPException(status_code=401, detail="Unauthorized user")

        # Fetch the client from the database
        client = appDb.query(Client).filter(Client.account_id == request.account_id).first()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Fetch the Client Settings
        client_settings = appDb.query(ClientSettings).filter(ClientSettings.account_id == request.account_id).first()

        # Update the client's subscription status and active modules
        client.subscribed = request.subscribed
        client.active_modules = request.active_modules or []
        client_settings.device_limit = request.device_limit if client_settings else 0

        # first check if any updates older than 45 days exist
        old_updates = adminDb.query(TrackUpdate).filter(
            TrackUpdate.updated_at < datetime.now(timezone.utc) - timedelta(days=45)).all()
        
        # If old updates exist, delete them
        if old_updates:
            for update in old_updates:
                adminDb.delete(update)
            adminDb.commit()

        await send_device1_update(request.account_id, 60, request.to_dict())

        # Create a track update entry
        track_update = TrackUpdate(
            update_data= request.to_dict(),
            updated_at=datetime.now(timezone.utc),
            updated_by=request.user_id,
            account_id=request.account_id
        )

        # Add the track update to the session
        adminDb.add(track_update)

        # Commit the changes to the database
        adminDb.commit()
        appDb.commit()

        # Return a success message
        return {"message": "Client subscription updated successfully"}
    
    except Exception as e:
        # Handle exceptions and return an error message
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")