# core/services/users.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from core import models, schemas, auth

# --- 1. SIGNUP LOGIC ---
def create_new_user(user: schemas.UserCreate, db: Session):
    # Check if email exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.hash_password(user.password)
    
    # Handle Roles
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
        
        # Upper case the code for consistency
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

# --- 2. AUTHENTICATION LOGIC ---
def authenticate_user(email: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not auth.verify_password(password, user.hashed_password):
        return None
    return user

# --- 3. FETCH EMPLOYEES ---
def get_company_employees(current_user: models.User, db: Session):
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