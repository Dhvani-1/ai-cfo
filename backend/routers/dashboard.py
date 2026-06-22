from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.transaction import Transaction
from models.user import User
from auth.dependencies import get_current_user

from analytics.cashflow import calculate_cashflow
from analytics.profit_loss import profit_loss
from analytics.category_analysis import category_summary

router = APIRouter()



@router.get("/cashflow")
def cashflow(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()

    return calculate_cashflow(transactions)

@router.get("/profit-loss")
def pnl(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()

    return profit_loss(transactions)

@router.get("/categories")
def categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()

    return category_summary(transactions)

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()

    return {
        "cashflow": calculate_cashflow(transactions),
        "profit_loss": profit_loss(transactions),
        "categories": category_summary(transactions)
    }