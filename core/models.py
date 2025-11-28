# models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from core.database import Base
import enum
from datetime import datetime

# --- NEW: Status Enum ---
# This creates a "controlled vocabulary" for our task status
class TaskStatus(str, enum.Enum):
    to_do = "To-Do"
    ongoing = "Ongoing"
    done = "Done"


# --- NEW: Company Table ---
class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    company_code = Column(String, unique=True, index=True, nullable=False)
    
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="company", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False) 

    company_id = Column(Integer, ForeignKey("companies.id"))
    
    company = relationship("Company", back_populates="users")
    
    # --- UPDATED: Personal Events die with the User ---
    events = relationship("Event", back_populates="owner", cascade="all, delete-orphan")
    
    
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="[Task.assignee_id]")
    created_tasks = relationship("Task", back_populates="task_creator", foreign_keys="[Task.owner_id]")


# --- NEW: Task Table ---
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.to_do, nullable=False)
    due_date = Column(DateTime, nullable=False)
    
    # Who created this task? (The Owner)
    owner_id = Column(Integer, ForeignKey("users.id"))
    # Who is this task assigned to? (The Employee)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    # Which company does this task belong to?
    company_id = Column(Integer, ForeignKey("companies.id"))
    
    # Relationships
    company = relationship("Company", back_populates="tasks")
    task_creator = relationship("User", back_populates="created_tasks", foreign_keys=[owner_id])
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    place = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    calendar_type = Column(String, default="general")
    
    # --- FIX 1: Add this ---
    # We make this nullable=True to avoid issues, but we'll always set it.
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True) 
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # --- FIX 2: Add this ---
    company = relationship("Company") # You can add back_populates="events" if you update the Company model
    
    owner = relationship("User", back_populates="events")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # We use Numeric(10, 2) for money. 
    # This means 10 digits total, with 2 digits after the decimal (e.g., 12345678.99)
    amount = Column(Numeric(10, 2), nullable=False) 
    
    type = Column(String, nullable=False) # "income" or "expense"
    category = Column(String, nullable=False) # e.g., "Food", "Salary"
    date = Column(DateTime, nullable=False)
    notes = Column(String, nullable=True)
    
    # --- Relationships ---
    # We link every transaction to a Company AND a User
    company_id = Column(Integer, ForeignKey("companies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User")
    company = relationship("Company")




# --- NOTEBOOK AGENT MODELS ---

class Notebook(Base):
    __tablename__ = "notebooks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # The 'cover' will store a CSS class or hex code (e.g., "blue", "#ff0000")
    cover = Column(String, default="blue") 
    
    # Ownership: Belongs to a Company, Created by a User
    company_id = Column(Integer, ForeignKey("companies.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    company = relationship("Company")
    owner = relationship("User")
    
    # Cascade Delete: If you burn the notebook, the notes inside burn too.
    notes = relationship("Note", back_populates="notebook", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    
    # "type" tells the frontend if it should draw a Text box or a Checklist
    type = Column(String, default="text") # 'text', 'checklist', 'photo'
    
    # This stores the actual data (simple text or JSON string for checklists)
    content = Column(String, nullable=True)
    
    # Visuals
    color = Column(String, default="white") 
    
    # Timestamps (Auto-generated)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Links
    notebook_id = Column(Integer, ForeignKey("notebooks.id"))
    notebook = relationship("Notebook", back_populates="notes")