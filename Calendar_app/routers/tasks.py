# routers/tasks.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core import models, schemas as schemas, auth
from core.dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/tasks", # This adds "/api/tasks" to all paths
    tags=["Tasks"]
)


# --- 1. CREATE TASK ---
# Path becomes: POST /api/tasks/
@router.post("/", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only owners can create tasks")
    
    employee = db.query(models.User).filter(
        models.User.id == task.assignee_id,
        models.User.company_id == current_user.company_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found in your company")

    new_task = models.Task(
        **task.dict(),
        owner_id=current_user.id,
        company_id=current_user.company_id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
    


# --- 3. UPDATE TASK ---
# Path becomes: PUT /api/tasks/{task_id}
@router.put("/{task_id}", response_model=schemas.Task)
def update_task_status(
    task_id: int,
    status: schemas.TaskStatus, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if current_user.role == "owner" and task.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role == "employee" and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    task.status = status
    db.commit()
    db.refresh(task)
    return task