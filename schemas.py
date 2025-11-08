# schemas.py
from models import TaskStatus
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List # Optional is for fields that can be empty (nullable)

# --- Event Schemas ---

# 1. Base Schema: These are the fields
#    common to both creating and reading.
class EventBase(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    place: Optional[str] = None # This field is optional, defaults to None
    notes: Optional[str] = None # Also optional
    calendar_type: str = "general" # Default to 'general'

# 2. Create Schema: This is the "form" our user
#    will fill out to *create* a new event.
#    It has all the fields from EventBase.
class EventCreate(EventBase):
    pass # "pass" means it has the exact same fields as EventBase

# 3. Read Schema: This is the "form" we will use
#    to *send* data back to the user. It adds the 'id'
#    that the database generates.
class Event(EventBase):
    id: int
    
    # This tells Pydantic to read the data even
    # if it's a database model (an "ORM" object)
    class Config:
        from_attributes = True



class TaskBase(BaseModel):
    title: str
    due_date: datetime
    status: TaskStatus = TaskStatus.to_do

class TaskCreate(TaskBase):
    assignee_id: int # The ID of the employee to assign this to

class Task(TaskBase):
    id: int
    owner_id: int
    assignee_id: int
    company_id: int

    class Config:
        from_attributes = True




class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    role: str # "owner" or "employee"
    
    # NEW: Add these optional fields
    companyName: Optional[str] = None
    companyCode: Optional[str] = None

class User(UserBase):
    id: int
    role: str
    company_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class Employee(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

# --- NEW: Token Schema ---
# This defines the "shape" of the "digital pass"
# we will send back to the user on login.
class Token(BaseModel):
    access_token: str
    token_type: str



class CalendarFeed(BaseModel):
    events: List[Event]
    tasks: List[Task]