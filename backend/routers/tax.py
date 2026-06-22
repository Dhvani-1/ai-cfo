import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.transaction import Transaction
from models.invoice import Invoice
from models.user import User
from auth.dependencies import get_current_user
from analytics.tax_summary import get_gst_summary
from analytics.tax_estimator import estimate_tax, generate_tax_insights

router = APIRouter()

@router.get("/gst-summary")
def gst_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).all()
    return get_gst_summary(invoices)

@router.get("/tax-estimate")
def tax_estimate(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return estimate_tax(transactions)

@router.get("/tax-insights")
def tax_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return generate_tax_insights(transactions)

@router.get("/tax-summary")
def tax_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).all()
    
    gst_data = get_gst_summary(invoices)
    estimate_data = estimate_tax(transactions)
    insights_data = generate_tax_insights(transactions)
    generated_at = datetime.datetime.utcnow().isoformat()
    disclaimer = "Tax calculations are estimates only and should not be considered professional or legal advice."
    
    return {
        "gst": gst_data,
        "estimate": estimate_data,
        "insights": insights_data,
        "generated_at": generated_at,
        "disclaimer": disclaimer
    }

