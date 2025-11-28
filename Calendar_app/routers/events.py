# routers/events.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core import models, schemas as schemas, auth
from core.dependencies import get_db, get_current_user 
from core.services import events as event_service
from core.services import tasks as task_service

router = APIRouter(
    tags=["Calendar Events"]
)

# --- CREATE EVENT ---
@router.post("/calendar/general/events", response_model=schemas.Event)
def create_event(
    event: schemas.EventCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Delegate to service
    return event_service.create_new_event(event, current_user, db)

# --- DELETE EVENT ---
@router.delete("/events/{event_id}")
def delete_event(
    event_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Delegate to service
    return event_service.delete_event_by_id(event_id, current_user, db)

# --- CALENDAR FEED ---
@router.get("/calendar/feed", response_model=schemas.CalendarFeed)
def get_calendar_feed(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    This endpoint is now purely a Coordinator.
    It asks the Event Service for events.
    It asks the Task Service for tasks.
    It bundles them together.
    """
    
    # 1. Get Events via Service 
    all_events = event_service.get_user_events(current_user, db)
    
    # 2. Get Tasks via Service (CLEAN NOW!)
    all_tasks = task_service.get_user_tasks(current_user, db)
        
    return {"events": all_events, "tasks": all_tasks}