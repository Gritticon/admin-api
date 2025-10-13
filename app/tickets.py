from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from database.session import get_admin_db
from app.verify_user import verify_user
from database.db_tickets import Ticket
from database.db_ticket_updates import TicketUpdate
from schema.s_ticket_updates import TicketUpdateSchema
from schema.s_tickets import TicketSchema


router = APIRouter(prefix="/admin-api/tickets", tags=["Ticket CRUD Operations"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#----------------------------------------------------- Create Ticket API ------------------------------------------------

@router.post('/create_ticket')
def create_ticket(
    user_id: int, 
    token: Annotated[str, Depends(oauth2_scheme)], 
    ticket_data: TicketSchema, 
    adminDb: Session = Depends(get_admin_db)
    ):
    # Validate the requested user
    if not verify_user(user_id, token, adminDb):
        raise HTTPException(status_code=401, detail="Unauthorized user")
    
    # Check if the ticket ID already exists
    existing_ticket = adminDb.query(Ticket).filter(Ticket.ticket_id == ticket_data.ticket_id).first()
    
    if existing_ticket:
        raise HTTPException(status_code=400, detail="Ticket ID already exists")
    
    try:
        # Create a new ticket ID if not provided
        if ticket_data.ticket_id == 0:
            last_ticket = adminDb.query(Ticket).order_by(Ticket.ticket_id.desc()).first()
            new_ticket_id = str(int(last_ticket.ticket_id) + 1) if last_ticket else "1"
            ticket_data.ticket_id = new_ticket_id
        
        # Create a new ticket instance
        ticket = Ticket(
            ticket_id=ticket_data.ticket_id,
            account_id=ticket_data.account_id,
            user_id=ticket_data.user_id,
            subject=ticket_data.subject,
            description=ticket_data.description,
            status=ticket_data.status,
            priority=ticket_data.priority,
            created_at=datetime.now(),
            contact_mode=ticket_data.contact_mode,
            clinet_name=ticket_data.client_name,
            client_phone=ticket_data.client_phone,
            clinet_email=ticket_data.client_email,
            attachment=ticket_data.attachment,
            notes=ticket_data.notes or None
        )

        # Add the new ticket to the session and commit
        adminDb.add(ticket)
        adminDb.commit()
        adminDb.refresh(ticket)

        ticket_data.ticket_id = ticket.ticket_id  
        ticket_data.created_at = ticket.created_at.isoformat()  

        # Return the created ticket data
        return {"message": "Ticket created successfully", "ticket": ticket_data.to_dict()}
    
    except Exception as e:
        adminDb.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")

#----------------------------------------------------- Get Ticket API ------------------------------------------------


@router.get('/get_all_opened_ticket')
def get_all_opened_ticket(user_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_admin_db)):

    # Validate the requested user
    if not verify_user(user_id, token, db):
        raise HTTPException(status_code=401, detail="Unauthorized user")
    
    # Fetch all opened tickets
    tickets = db.query(Ticket).filter(Ticket.status != 0).all()
    
    if not tickets:
        return {"tickets": []}
    
    # Return the list of tickets as dictionaries
    tickets = [TicketSchema(
        ticket_id=ticket.ticket_id,
        account_id=ticket.account_id,
        user_id=ticket.user_id,
        subject=ticket.subject,
        description=ticket.description,
        status=ticket.status,
        priority=ticket.priority,
        created_at=ticket.created_at.isoformat(),
        contact_mode=ticket.contact_mode,
        client_name=ticket.clinet_name,
        client_phone=ticket.client_phone,
        client_email=ticket.clinet_email,
        attachment=ticket.attachment,
        notes=ticket.notes
    ).to_dict() for ticket in tickets]
    
    return {"tickets": tickets}


#---------------------------------------------- Get Specific Client Tickets API ------------------------------------------

@router.get('/get_client_tickets')
def get_client_tickets(client_id: int, user_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_admin_db)):

    # Validate the requested user
    if not verify_user(user_id, token, db):
        raise HTTPException(status_code=401, detail="Unauthorized user")
    
    # Fetch tickets for the specified client
    tickets = db.query(Ticket).filter(Ticket.account_id == client_id).all()
    
    if not tickets:
        raise HTTPException(status_code=404, detail="No tickets found for this client")
    
    # Return the list of tickets as dictionaries
    if not tickets:
        raise HTTPException(status_code=404, detail="No tickets found for this client")
    
    # Return the list of tickets as dictionaries
    tickets_list = []

    for ticket in tickets:
        ticket = TicketSchema(
            ticket_id=ticket.ticket_id,
            account_id=ticket.account_id,
            user_id=ticket.user_id,
            subject=ticket.subject,
            description=ticket.description,
            status=ticket.status,
            priority=ticket.priority,
            created_at=ticket.created_at.isoformat(),
            contact_mode=ticket.contact_mode,
            client_name=ticket.clinet_name,
            client_phone=ticket.client_phone,
            client_email=ticket.clinet_email,
            attachment=ticket.attachment,
            notes=ticket.notes
        )
        tickets_list.append(ticket.to_dict())
    
    return {"tickets": tickets_list}

#----------------------------------------------------- Get Ticket Updats API ------------------------------------------------


@router.get('/get_ticket_updates')
def get_ticket_updates(ticket_id: str, user_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_admin_db)):

    # Validate the requested user
    if not verify_user(user_id, token, db):
        raise HTTPException(status_code=401, detail="Unauthorized user")
    
    # Fetch updates for the specified ticket
    updates = db.query(TicketUpdate).filter(TicketUpdate.ticket_id == ticket_id).all()
    
    if not updates:
        raise HTTPException(status_code=404, detail="No updates found for this ticket")
    
    # Return the list of updates as dictionaries
    updates_list = []

    for update in updates:
        update = TicketUpdateSchema(
                ticket_id=update.ticket_id,
                updated_by=update.user_id,
                description=update.description,
                attachment=update.attachment,
                created_at= update.created_at.isoformat(),
                contact_mode=update.contact_mode,
                notes=update.notes
            )
        updates_list.append(update.to_dict())

    return {"updates": updates_list}

#----------------------------------------------------- Create Update API ------------------------------------------------


@router.post('/create_update')
def create_update(user_id: int, token: Annotated[str, Depends(oauth2_scheme)], update_data: TicketUpdateSchema, db: Session = Depends(get_admin_db)):
    # Validate the requested user
    if not verify_user(user_id, token, db):
        raise HTTPException(status_code=401, detail="Unauthorized user")
    
    # Check if the ticket ID exists
    existing_ticket = db.query(Ticket).filter(Ticket.ticket_id == update_data.ticket_id).first()
    
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    try:
        # Create a new ticket update instance
        update = TicketUpdate(
            ticket_id=update_data.ticket_id,
            user_id=user_id,
            description=update_data.description,
            attachment=update_data.attachment,
            created_at=datetime.now(),
            contact_mode=update_data.contact_mode,
            notes=update_data.notes or None
        )

        # Add the new update to the session and commit
        db.add(update)

        existing_ticket.status = 2 

        db.commit()
        db.refresh(update)

        update_data.created_at = update.created_at.isoformat()

        return {"message": "Update created successfully", "update": update_data.to_dict()}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating update: {str(e)}")


#-------------------------------------------- Update Ticket Status and Priority API -----------------------------------------

@router.put('/update_ticket_status')
def update_ticket_status(ticket_id: int, user_id: int, token: Annotated[str, Depends(oauth2_scheme)], status: int, priority: int, db: Session = Depends(get_admin_db)):
    # Validate the requested user
    if not verify_user(user_id, token, db):
        raise HTTPException(status_code=401, detail="Unauthorized user")
    
    # Fetch the ticket to update
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    try:
        # Update the ticket status and priority
        ticket.status = status
        ticket.priority = priority
        
        # Commit the changes to the database
        db.commit()
        db.refresh(ticket)

        return {"message": "Ticket updated successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {str(e)}")
