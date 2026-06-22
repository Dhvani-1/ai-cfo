from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.transaction import Transaction
from models.user import User
from auth.dependencies import get_current_user

from analytics.forecast import (
    build_monthly_series,
    forecast_income_ma,
    forecast_expenses_ma,
    predict_income_trend,
    predict_expense_trend,
    calculate_cash_runway,
    forecast_summary
)

router = APIRouter()

@router.get("/monthly-series")
def monthly_series(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return build_monthly_series(transactions)

@router.get("/forecast")
def forecast(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return forecast_summary(transactions)

@router.get("/future-income")
def future_income(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return forecast_income_ma(transactions)

@router.get("/future-expenses")
def future_expenses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return forecast_expenses_ma(transactions)

@router.get("/cash-runway")
def cash_runway(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return calculate_cash_runway(transactions)

@router.get("/trend-analysis")
def trend_analysis(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return {
        "income": predict_income_trend(transactions),
        "expenses": predict_expense_trend(transactions)
    }

