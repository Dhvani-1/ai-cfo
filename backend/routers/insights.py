from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.transaction import Transaction
from models.user import User
from auth.dependencies import get_current_user

from analytics.monthly_summary import (
    get_monthly_summary,
    get_top_expenses,
    get_top_income,
    get_category_ranking
)
from analytics.anomalies import get_anomalies
from analytics.insights import generate_insights

router = APIRouter()

@router.get("/monthly-summary")
def monthly_summary(month: str = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return get_monthly_summary(transactions, month=month)

@router.get("/top-expenses")
def top_expenses(limit: int = Query(5), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return get_top_expenses(transactions, limit=limit)

@router.get("/top-income")
def top_income(limit: int = Query(5), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return get_top_income(transactions, limit=limit)

@router.get("/category-ranking")
def category_ranking(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return get_category_ranking(transactions)

@router.get("/anomalies")
def anomalies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return get_anomalies(transactions)

@router.get("/insights")
def insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return generate_insights(transactions)

