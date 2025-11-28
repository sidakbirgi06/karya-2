# core/services/notebooks.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from core import models, schemas

# --- 1. NOTEBOOK LOGIC (The Shelves) ---

def create_new_notebook(notebook: schemas.NotebookCreate, user: models.User, db: Session):
    # Logic: Notebooks belong to the Company, created by the User.
    db_notebook = models.Notebook(
        **notebook.dict(),
        company_id=user.company_id,
        owner_id=user.id
    )
    db.add(db_notebook)
    db.commit()
    db.refresh(db_notebook)
    return db_notebook

def get_all_notebooks(user: models.User, db: Session):
    # Logic: Show all notebooks in the user's company
    return db.query(models.Notebook).filter(
        models.Notebook.company_id == user.company_id
    ).all()

def get_notebook_by_id(notebook_id: int, user: models.User, db: Session):
    # Logic: Find the notebook and ensure it belongs to the user's company
    notebook = db.query(models.Notebook).filter(
        models.Notebook.id == notebook_id,
        models.Notebook.company_id == user.company_id
    ).first()
    
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    return notebook


# --- 2. NOTE LOGIC (The Cards) ---

def create_note_in_notebook(notebook_id: int, note: schemas.NoteCreate, user: models.User, db: Session):
    # Security Check: Does this notebook actually exist in this company?
    # We re-use the function above to do the check.
    get_notebook_by_id(notebook_id, user, db)
    
    # Create the note
    db_note = models.Note(
        **note.dict(),
        notebook_id=notebook_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_notes_for_notebook(notebook_id: int, user: models.User, db: Session):
    # Security Check first
    get_notebook_by_id(notebook_id, user, db)
    
    # Fetch notes (newest first usually looks better)
    return db.query(models.Note).filter(
        models.Note.notebook_id == notebook_id
    ).order_by(models.Note.created_at.desc()).all()




def delete_note_by_id(note_id: int, user: models.User, db: Session):
    # 1. Find the note
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    # 2. Security Check: Does the user own the Notebook this note belongs to?
    # We join the tables to check the company_id of the parent notebook
    notebook = db.query(models.Notebook).filter(
        models.Notebook.id == note.notebook_id,
        models.Notebook.company_id == user.company_id
    ).first()
    
    if not notebook:
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")

    # 3. Delete it
    db.delete(note)
    db.commit()
    return {"message": "Note deleted"}


# core/services/notebooks.py (Add this to the bottom)

def update_note_content(note_id: int, note_update: schemas.NoteUpdate, user: models.User, db: Session):
    # 1. Find the note
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    # 2. Check Permission (via Notebook ownership)
    # We ensure the note belongs to a notebook in the user's company
    notebook = db.query(models.Notebook).filter(
        models.Notebook.id == db_note.notebook_id,
        models.Notebook.company_id == user.company_id
    ).first()
    if not notebook:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 3. Update fields if they are provided (checking for None allows partial updates)
    if note_update.title is not None:
        db_note.title = note_update.title
    if note_update.content is not None:
        db_note.content = note_update.content
    
    db.commit()
    db.refresh(db_note)
    return db_note