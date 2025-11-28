# schemas.py
from .models import TaskStatus
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


class TransactionBase(BaseModel):
    amount: float
    type: str # "income" or "expense"
    category: str
    date: datetime
    notes: Optional[str] = None

# 2. Create Schema (What the form sends us)
class TransactionCreate(TransactionBase):
    pass 

# 3. Reading Schema (What we send back, including IDs)
class Transaction(TransactionBase):
    id: int
    user_id: int
    company_id: int
    
    class Config:
        from_attributes = True

# 4. Dashboard Schema (The calculated totals)
class DashboardData(BaseModel):
    total_income: float
    total_expense: float
    balance: float



class CategoryStat(BaseModel):
    category: str
    total: float

# The complete report for the date range
class SummaryReport(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    # A list of category stats for our charts
    expense_by_category: List[CategoryStat]
    income_by_category: List[CategoryStat]




# --- NOTEBOOK AGENT SCHEMAS ---

# 1. NOTE SCHEMAS (The Cards)
class NoteBase(BaseModel):
    title: Optional[str] = None
    type: str = "text"   # "text", "checklist", "photo"
    content: Optional[str] = None # Stores text or JSON string
    color: str = "white"

class NoteCreate(NoteBase):
    pass # Same fields as Base for creation

class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    notebook_id: int # Link back to the parent shelf

    class Config:
        from_attributes = True # Allows reading from ORM model

# 2. NOTEBOOK SCHEMAS (The Shelves)
class NotebookBase(BaseModel):
    name: str
    cover: str = "blue" # Class name or Hex color

class NotebookCreate(NotebookBase):
    pass 

class Notebook(NotebookBase):
    id: int
    company_id: int
    owner_id: int
    
    # This is the magic: It will automatically fetch all notes inside!
    notes: List[Note] = [] 

    class Config:
        from_attributes = True



class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None