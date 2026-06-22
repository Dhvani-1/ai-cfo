from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.transaction import Transaction
from models.user import User
from auth.dependencies import get_current_user

from analytics.health_score import calculate_health_score, get_financial_grade
from analytics.ratios import calculate_savings_ratio, calculate_expense_ratio
from analytics.risk_analysis import analyze_risk
from analytics.recommendations import generate_recommendations

router = APIRouter()

@router.get("/health-score")
def health_score(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return calculate_health_score(transactions)

@router.get("/financial-grade")
def financial_grade(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    score_data = calculate_health_score(transactions)
    return get_financial_grade(score_data["health_score"])

@router.get("/risk-analysis")
def risk_analysis(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return analyze_risk(transactions)

@router.get("/savings-ratio")
def savings_ratio(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return calculate_savings_ratio(transactions)

@router.get("/expense-ratio")
def expense_ratio(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return calculate_expense_ratio(transactions)

@router.get("/recommendations")
def recommendations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return generate_recommendations(transactions)

@router.get("/financial-health")
def financial_health(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    score_data = calculate_health_score(transactions)
    grade_info = get_financial_grade(score_data["health_score"])
    risk_info = analyze_risk(transactions)
    savings = calculate_savings_ratio(transactions)
    expense = calculate_expense_ratio(transactions)
    recs = generate_recommendations(transactions)

    return {
        "health_score": {
            "score": score_data["health_score"],
            "components": score_data["components"]
        },
        "grade": grade_info,
        "risk": risk_info,
        "ratios": {
            "savings_ratio": savings,
            "expense_ratio": expense
        },
        "recommendations": recs
    }

