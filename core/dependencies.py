# dependencies.py

# --- 1. Imports ---
# We need to import all the tools our functions will use
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core import models, schemas as schemas, database, auth

# --- 2. The "Policeman" ---
# We move this here from main.py because get_current_user needs it
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 

# --- 3. The "Database Key" Helper ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 4. The "Locksmith" Helper ---
def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    payload = auth.verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user