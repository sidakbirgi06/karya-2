# Finance_app/routers/finance.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from core import models, schemas
from core.dependencies import get_db, get_current_user
from core.services import finance as finance_service

router = APIRouter(
    prefix="/api/finance",
    tags=["Finance"]
)

# --- 1. CREATE TRANSACTION ---
@router.post("/transactions", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return finance_service.create_transaction(transaction, current_user, db)

# --- 2. GET DASHBOARD ---
@router.get("/dashboard", response_model=schemas.DashboardData)
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return finance_service.get_dashboard_stats(current_user, db)

# --- 3. GET TRANSACTION LIST ---
@router.get("/transactions", response_model=List[schemas.Transaction])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return finance_service.get_transactions_list(current_user, db)

# --- 4. GET SUMMARY REPORT ---
@router.get("/summary", response_model=schemas.SummaryReport)
def get_summary_report(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return finance_service.generate_summary_report(start_date, end_date, current_user, db)