# core/services/tasks.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from core import models, schemas

# --- 1. CREATE TASK ---
def create_new_task(task: schemas.TaskCreate, user: models.User, db: Session):
    if user.role != "owner":
        raise HTTPException(status_code=403, detail="Only owners can create tasks")
    
    # Check if the employee belongs to this company
    employee = db.query(models.User).filter(
        models.User.id == task.assignee_id,
        models.User.company_id == user.company_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found in your company")

    new_task = models.Task(
        **task.dict(),
        owner_id=user.id,
        company_id=user.company_id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# --- 2. UPDATE TASK STATUS ---
def update_task_status(task_id: int, status: schemas.TaskStatus, user: models.User, db: Session):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Permission Logic:
    # 1. Owners can update any task in their company
    # 2. Employees can only update tasks assigned to them
    if user.role == "owner": 
        if task.company_id != user.company_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif user.role == "employee":
        if task.assignee_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
    task.status = status
    db.commit()
    db.refresh(task)
    return task

# --- 3. GET TASKS (For the Feed) ---
def get_user_tasks(user: models.User, db: Session):
    """Fetches tasks based on whether the user is an Owner or Employee"""
    if user.role == "owner":
        # Owners see all tasks for their company
        return db.query(models.Task).filter(
            models.Task.company_id == user.company_id
        ).all()
    else:
        # Employees get only tasks assigned to them
        return db.query(models.Task).filter(
            models.Task.assignee_id == user.id
        ).all()