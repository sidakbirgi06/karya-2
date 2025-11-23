# Finance_app/routers/finance.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from core import models, schemas
from core.dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/finance", # All endpoints will start with this
    tags=["Finance"]
)

# --- 1. CREATE TRANSACTION ---
@router.post("/transactions", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # RULE: Only Owners can record "Income"
    if transaction.type == "income" and current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only owners can add income")
    
    # Create the transaction
    db_transaction = models.Transaction(
        **transaction.dict(),
        user_id=current_user.id,
        company_id=current_user.company_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# --- 2. GET DASHBOARD (Totals) ---
@router.get("/dashboard", response_model=schemas.DashboardData)
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # RULE: Only Owners can see the dashboard
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized to view company financials")

    # Calculate Total Income
    income = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.company_id == current_user.company_id,
        models.Transaction.type == "income"
    ).scalar() or 0.0

    # Calculate Total Expense
    expense = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.company_id == current_user.company_id,
        models.Transaction.type == "expense"
    ).scalar() or 0.0

    # Calculate Balance
    balance = float(income) - float(expense)
    
    return {
        "total_income": float(income),
        "total_expense": float(expense),
        "balance": balance
    }

# --- 3. GET TRANSACTION LIST ---
@router.get("/transactions", response_model=List[schemas.Transaction])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role == "owner":
        # Owners see ALL transactions for the company
        transactions = db.query(models.Transaction).filter(
            models.Transaction.company_id == current_user.company_id
        ).order_by(models.Transaction.date.desc()).all()
    else:
        # Employees see only THEIR OWN expenses
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.id
        ).order_by(models.Transaction.date.desc()).all()
    
    return transactions


# --- 4. GET SUMMARY REPORT (New) ---
@router.get("/summary", response_model=schemas.SummaryReport)
def get_summary_report(
    start_date: str, # Format: YYYY-MM-DD
    end_date: str,   # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Base Query: Filter by User/Company AND Date Range
    query = db.query(models.Transaction).filter(
        models.Transaction.date >= start_date,
        models.Transaction.date <= end_date
    )

    if current_user.role == "owner":
        query = query.filter(models.Transaction.company_id == current_user.company_id)
    else:
        query = query.filter(models.Transaction.user_id == current_user.id)

    transactions = query.all()

    # 2. Calculate Totals in Python (Simple & Fast)
    total_inc = 0.0
    total_exp = 0.0
    inc_cats = {} # Dictionary to group Income: {"Salary": 5000, ...}
    exp_cats = {} # Dictionary to group Expense: {"Food": 50, ...}

    for t in transactions:
        amt = float(t.amount)
        if t.type == "income":
            total_inc += amt
            # Add to category grouping
            inc_cats[t.category] = inc_cats.get(t.category, 0) + amt
        else:
            total_exp += amt
            # Add to category grouping
            exp_cats[t.category] = exp_cats.get(t.category, 0) + amt

    # 3. Convert Dictionaries to Lists for the Schema
    # This turns {"Food": 50} into [{"category": "Food", "total": 50}]
    expense_list = [schemas.CategoryStat(category=c, total=t) for c, t in exp_cats.items()]
    income_list = [schemas.CategoryStat(category=c, total=t) for c, t in inc_cats.items()]

    return {
        "total_income": total_inc,
        "total_expense": total_exp,
        "balance": total_inc - total_exp,
        "expense_by_category": expense_list,
        "income_by_category": income_list
    }