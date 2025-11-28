# core/services/finance.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from core import models, schemas
from typing import List, Dict

# --- 1. CREATE TRANSACTION ---
def create_transaction(transaction: schemas.TransactionCreate, user: models.User, db: Session):
    # Rule: Only Owners can add Income
    if transaction.type == "income" and user.role != "owner":
        raise HTTPException(status_code=403, detail="Only owners can add income")
    
    db_transaction = models.Transaction(
        **transaction.dict(),
        user_id=user.id,
        company_id=user.company_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# --- 2. GET TRANSACTIONS (List) ---
def get_transactions_list(user: models.User, db: Session):
    if user.role == "owner":
        # Owners see ALL transactions for the company
        return db.query(models.Transaction).filter(
            models.Transaction.company_id == user.company_id
        ).order_by(models.Transaction.date.desc()).all()
    else:
        # Employees see only THEIR OWN expenses
        return db.query(models.Transaction).filter(
            models.Transaction.user_id == user.id
        ).order_by(models.Transaction.date.desc()).all()

# --- 3. CALCULATE DASHBOARD STATS ---
def get_dashboard_stats(user: models.User, db: Session):
    if user.role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized to view company financials")

    # Sum Income
    income = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.company_id == user.company_id,
        models.Transaction.type == "income"
    ).scalar() or 0.0

    # Sum Expense
    expense = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.company_id == user.company_id,
        models.Transaction.type == "expense"
    ).scalar() or 0.0

    return {
        "total_income": float(income),
        "total_expense": float(expense),
        "balance": float(income) - float(expense)
    }

# --- 4. GENERATE SUMMARY REPORT ---
def generate_summary_report(start_date: str, end_date: str, user: models.User, db: Session):
    # Base Query
    query = db.query(models.Transaction).filter(
        models.Transaction.date >= start_date,
        models.Transaction.date <= end_date
    )

    if user.role == "owner":
        query = query.filter(models.Transaction.company_id == user.company_id)
    else:
        query = query.filter(models.Transaction.user_id == user.id)

    transactions = query.all()

    # Calculate Totals
    total_inc = 0.0
    total_exp = 0.0
    inc_cats: Dict[str, float] = {} 
    exp_cats: Dict[str, float] = {} 

    for t in transactions:
        amt = float(t.amount)
        if t.type == "income":
            total_inc += amt
            inc_cats[t.category] = inc_cats.get(t.category, 0) + amt
        else:
            total_exp += amt
            exp_cats[t.category] = exp_cats.get(t.category, 0) + amt

    # Format for Schema
    expense_list = [schemas.CategoryStat(category=c, total=t) for c, t in exp_cats.items()]
    income_list = [schemas.CategoryStat(category=c, total=t) for c, t in inc_cats.items()]

    return {
        "total_income": total_inc,
        "total_expense": total_exp,
        "balance": total_inc - total_exp,
        "expense_by_category": expense_list,
        "income_by_category": income_list
    }