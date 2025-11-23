# routers/events.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core import models, schemas as schemas, auth
from core.dependencies import get_db, get_current_user # Our toolbox

router = APIRouter(
    tags=["Calendar Events"] # Group for API docs
)



# --- 3. CREATE EVENT ---
@router.post("/calendar/general/events", response_model=schemas.Event)
def create_event(
    event: schemas.EventCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    db_event = models.Event(**event.dict())
    db_event.company_id = current_user.company_id
    
    if event.calendar_type == "personal":
        db_event.owner_id = current_user.id
    elif event.calendar_type == "general":
        if current_user.role != "owner":
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


# --- 4. DELETE EVENT ---
@router.delete("/events/{event_id}")
def delete_event(
    event_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    event_to_delete = db.query(models.Event).filter(
        models.Event.id == event_id
    ).first()

    if not event_to_delete:
        raise HTTPException(status_code=404, detail="Event not found")
        
    if event_to_delete.calendar_type == "personal":
        if event_to_delete.owner_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this event"
            )
    elif event_to_delete.calendar_type == "general":
        if current_user.role != "owner":
            raise HTTPException(
                status_code=403, detail="Not authorized to delete general events"
            )
        # This is a good extra check:
        if event_to_delete.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(event_to_delete)
    db.commit()
    return {"message": "Event deleted successfully"}



# --- NEW: "SUPER" ENDPOINT FOR THE CALENDAR FEED ---
@router.get("/calendar/feed", response_model=schemas.CalendarFeed)
def get_calendar_feed(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    This single endpoint securely fetches all events and tasks
    for the current user in one API call.
    """
    
    # --- 1. Get Events ---
    # Get all "general" events for the user's company
    general_events = db.query(models.Event).filter(
        models.Event.calendar_type == "general",
        models.Event.company_id == current_user.company_id
    ).all()
    
    # Get all "personal" events for the user
    personal_events = db.query(models.Event).filter(
        models.Event.calendar_type == "personal",
        models.Event.owner_id == current_user.id
    ).all()
    
    all_events = general_events + personal_events
    
    # --- 2. Get Tasks ---
    all_tasks = []
    if current_user.role == "owner":
        # Owners get all tasks for their company
        all_tasks = db.query(models.Task).filter(
            models.Task.company_id == current_user.company_id
        ).all()
    else:
        # Employees get only tasks assigned to them
        all_tasks = db.query(models.Task).filter(
            models.Task.assignee_id == current_user.id
        ).all()
        
    # --- 3. Return a single response ---
    return {"events": all_events, "tasks": all_tasks}



# --- 3. GET EMPLOYEE LIST ---
# (Paste this back in)
@router.get("/api/my-employees", response_model=List[schemas.Employee])
def get_employees(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(
            status_code=403, detail="You do not have permission to view employees"
        )
    company_id = current_user.company_id
    if not company_id:
        raise HTTPException(status_code=404, detail="You are not associated with a company")

    employees = db.query(models.User).filter(
        models.User.company_id == company_id,
        models.User.role == "employee"
    ).all()
    return employees