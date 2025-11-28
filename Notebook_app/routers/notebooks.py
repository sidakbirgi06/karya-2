# Notebook_app/routers/notebooks.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core import models, schemas
from core.dependencies import get_db, get_current_user
from core.services import notebooks as notebook_service

router = APIRouter(
    prefix="/api/notebooks",
    tags=["Notebooks"]
)

# --- 1. NOTEBOOK ENDPOINTS (The Shelves) ---

@router.post("/", response_model=schemas.Notebook)
def create_notebook(
    notebook: schemas.NotebookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return notebook_service.create_new_notebook(notebook, current_user, db)

@router.get("/", response_model=List[schemas.Notebook])
def get_notebooks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return notebook_service.get_all_notebooks(current_user, db)

@router.get("/{notebook_id}", response_model=schemas.Notebook)
def get_one_notebook(
    notebook_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return notebook_service.get_notebook_by_id(notebook_id, current_user, db)


# --- 2. NOTE ENDPOINTS (The Cards) ---

@router.post("/{notebook_id}/notes", response_model=schemas.Note)
def create_note(
    notebook_id: int,
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return notebook_service.create_note_in_notebook(notebook_id, note, current_user, db)

@router.get("/{notebook_id}/notes", response_model=List[schemas.Note])
def get_notes(
    notebook_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return notebook_service.get_notes_for_notebook(notebook_id, current_user, db)




@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return notebook_service.delete_note_by_id(note_id, current_user, db)



@router.put("/notes/{note_id}", response_model=schemas.Note)
def update_note(
    note_id: int,
    note: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return notebook_service.update_note_content(note_id, note, current_user, db)