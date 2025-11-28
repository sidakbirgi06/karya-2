# routers/users.py

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from core import models, schemas as schemas, auth
from core.dependencies import get_db, get_current_user 
from core.services import users as user_service

router = APIRouter(tags=["Users & Auth"])

# --- 1. SIGNUP (Unchanged) ---
@router.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return user_service.create_new_user(user, db)


# --- 2. LOGIN (UPDATED) ---
@router.post("/login")
def login_for_access_token(
    response: Response,  # We need this to set the cookie
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # 1. Authenticate via Service
    user = user_service.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    # 2. Create Token
    access_token_data = {"sub": user.email, "id": user.id, "role": user.role}
    access_token = auth.create_access_token(data=access_token_data)
    
    # 3. SET THE SECURE COOKIE
    # httponly=True  -> JavaScript CANNOT read this (prevents XSS)
    # samesite='lax' -> Protects against CSRF attacks
    # secure=False   -> Set to True if using HTTPS (we use False for localhost)
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        samesite='lax',
        secure=False 
    )
    
    return {"message": "Login successful"}


# --- 3. LOGOUT (NEW) ---
@router.post("/logout")
def logout(response: Response):
    # To logout, we simply delete the cookie
    response.delete_cookie("access_token")
    return {"message": "Logged out"}


# --- 4. GET EMPLOYEE LIST (Unchanged) ---
@router.get("/api/my-employees", response_model=List[schemas.Employee])
def get_employees(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return user_service.get_company_employees(current_user, db)



# Add this at the bottom of routers/users.py

@router.get("/api/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "company_id": current_user.company_id
    }