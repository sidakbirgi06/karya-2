# models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

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
    
    # This links a Company to its list of Users and Tasks
    users = relationship("User", back_populates="company")
    tasks = relationship("Task", back_populates="company")


# --- UPDATED: User Table ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False) # "owner" or "employee"

    # This is the new "link" to the Company table
    company_id = Column(Integer, ForeignKey("companies.id"))
    
    # This creates the virtual link for Python
    company = relationship("Company", back_populates="users")
    
    # Links to a user's *personal* events (no change)
    events = relationship("Event", back_populates="owner")
    
    # Links to all tasks *assigned* to this user
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="[Task.assignee_id]")
    
    # Links to all tasks *created* by this user (if they are an owner)
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