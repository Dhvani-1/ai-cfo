import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.invoice import Invoice
from models.user import User
from auth.dependencies import get_current_user
from ocr.invoice_parser import extract_text
from ocr.invoice_extractor import extract_invoice_fields
from ocr.invoice_classifier import categorize_vendor

router = APIRouter()

@router.post("/upload-invoice")
async def upload_invoice(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    os.makedirs("uploads/invoices", exist_ok=True)
    file_path = f"uploads/invoices/{file.filename}"
    
    # Save the file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Extract text using parser (with pdfplumber / easyocr / .txt fallback)
    raw_text = extract_text(file_path)
    
    # Extract fields using regex
    fields = extract_invoice_fields(raw_text)
    
    # Categorize vendor
    category = categorize_vendor(fields["vendor"])
    
    # Check for duplicate: vendor, invoice_date, total_amount for this user
    existing = db.query(Invoice).filter(
        Invoice.vendor == fields["vendor"],
        Invoice.invoice_date == fields["invoice_date"],
        Invoice.total_amount == fields["total_amount"],
        Invoice.user_id == current_user.id
    ).first()
    
    if existing:
        return {
            "message": "Invoice already exists",
            "duplicate": True
        }
        
    # Create database record
    invoice = Invoice(
        vendor=fields["vendor"],
        invoice_number=fields["invoice_number"],
        invoice_date=fields["invoice_date"],
        total_amount=fields["total_amount"],
        gst_number=fields["gst_number"],
        category=category,
        file_path=file_path,
        ocr_text=raw_text,
        user_id=current_user.id
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

@router.get("/invoices")
def get_invoices(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Invoice).filter(Invoice.user_id == current_user.id).all()

@router.get("/invoice/{id}")
def get_invoice(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Query invoice by ID
    invoice = db.query(Invoice).filter(Invoice.id == id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Enforce ownership boundary - returning 404 instead of 403 on Multi-User Leakage
    if invoice.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    return invoice

@router.delete("/invoice/{id}")
def delete_invoice(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Query invoice by ID
    invoice = db.query(Invoice).filter(Invoice.id == id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Enforce ownership boundary - returning 404 instead of 403 on Multi-User Leakage
    if invoice.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    # Delete uploaded file from disk (ignore missing file errors)
    if invoice.file_path:
        try:
            if os.path.exists(invoice.file_path):
                os.remove(invoice.file_path)
        except Exception:
            pass
            
    db.delete(invoice)
    db.commit()
    return {"message": "Invoice deleted successfully"}

@router.get("/invoice-summary")
def get_invoice_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from sqlalchemy import func
    
    total_invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).count()
    total_spend_raw = db.query(func.sum(Invoice.total_amount)).filter(Invoice.user_id == current_user.id).scalar()
    total_spend = round(total_spend_raw, 2) if total_spend_raw is not None else 0.0
    
    # Calculate top vendor (by total spend grouped by vendor) for this user
    top_vendor = None
    vendor_row = db.query(
        Invoice.vendor,
        func.sum(Invoice.total_amount)
    ).filter(
        Invoice.user_id == current_user.id,
        Invoice.vendor.isnot(None)
    ).group_by(Invoice.vendor).order_by(func.sum(Invoice.total_amount).desc()).first()
    
    if vendor_row:
        top_vendor = vendor_row[0]
        
    # Calculate top category (by total spend grouped by category) for this user
    top_category = None
    category_row = db.query(
        Invoice.category,
        func.sum(Invoice.total_amount)
    ).filter(
        Invoice.user_id == current_user.id,
        Invoice.category.isnot(None)
    ).group_by(Invoice.category).order_by(func.sum(Invoice.total_amount).desc()).first()
    
    if category_row:
        top_category = category_row[0]
        
    return {
        "total_invoices": total_invoices,
        "total_spend": total_spend,
        "top_vendor": top_vendor,
        "top_category": top_category
    }
