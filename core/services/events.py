# core/services/events.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from core import models, schemas

# --- 1. CREATE EVENT ---
def create_new_event(event: schemas.EventCreate, user: models.User, db: Session):
    # Prepare the DB object
    db_event = models.Event(**event.dict())
    db_event.company_id = user.company_id
    
    # Logic: Personal vs General
    if event.calendar_type == "personal":
        db_event.owner_id = user.id
    elif event.calendar_type == "general":
        if user.role != "owner":
            raise HTTPException(
                status_code=403, detail="Not authorized to create general events"
            )
        db_event.owner_id = None
    else:
        raise HTTPException(status_code=400, detail="Invalid calendar_type")

    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# --- 2. DELETE EVENT ---
def delete_event_by_id(event_id: int, user: models.User, db: Session):
    event_to_delete = db.query(models.Event).filter(
        models.Event.id == event_id
    ).first()

    if not event_to_delete:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # Permission Logic
    if event_to_delete.calendar_type == "personal":
        if event_to_delete.owner_id != user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this event"
            )
    elif event_to_delete.calendar_type == "general":
        if user.role != "owner":
            raise HTTPException(
                status_code=403, detail="Not authorized to delete general events"
            )
        # Extra safety check:
        if event_to_delete.company_id != user.company_id:
            raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(event_to_delete)
    db.commit()
    return {"message": "Event deleted successfully"}

# --- 3. GET EVENTS (For the Feed) ---
def get_user_events(user: models.User, db: Session):
    """Fetches both General (Company) and Personal events for the user"""
    
    # 1. General Events (Company-wide)
    general_events = db.query(models.Event).filter(
        models.Event.calendar_type == "general",
        models.Event.company_id == user.company_id
    ).all()
    
    # 2. Personal Events (User-specific)
    personal_events = db.query(models.Event).filter(
        models.Event.calendar_type == "personal",
        models.Event.owner_id == user.id
    ).all()
    
    return general_events + personal_events