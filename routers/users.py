# routers/users.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth
from dependencies import get_db, get_current_user # Our new toolbox

# This is the "router" variable that main.py is looking for
router = APIRouter(
    tags=["Users & Auth"] # This groups our API docs
)


# --- 1. SIGNUP ---
@router.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.hash_password(user.password)
    
    if user.role == "owner":
        if not user.companyName:
            raise HTTPException(status_code=400, detail="Company name is required for owners")
        new_code = auth.generate_company_code()
        new_company = models.Company(name=user.companyName, company_code=new_code)
        db.add(new_company)
        db.commit()
        db.refresh(new_company)
        new_user = models.User(
            email=user.email,
            hashed_password=hashed_password,
            role="owner",
            company_id=new_company.id
        )
    elif user.role == "employee":
        if not user.companyCode:
            raise HTTPException(status_code=400, detail="Company code is required for employees")
        company = db.query(models.Company).filter(
            models.Company.company_code == user.companyCode.upper()
        ).first()
        if not company:
            raise HTTPException(status_code=404, detail="Invalid Company Code")
        new_user = models.User(
            email=user.email,
            hashed_password=hashed_password,
            role="employee",
            company_id=company.id
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid role")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# --- 2. LOGIN ---
@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401, detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_data = {
        "sub": user.email,
        "id": user.id,
        "role": user.role
    }
    access_token = auth.create_access_token(data=access_token_data)
    return {"access_token": access_token, "token_type": "bearer"}


# --- 3. GET EMPLOYEE LIST ---
@router.get("/api/my-employees", response_model=List[schemas.Employee])
def get_employees(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(
            status_code=403, detail="You do not have permission to view employees"
        )
    company_id = current_user.company_id
    if not company_id:
        raise HTTPException(status_code=404, detail="You are not associated with a company")

    employees = db.query(models.User).filter(
        models.User.company_id == company_id,
        models.User.role == "employee"
    ).all()
    return employees