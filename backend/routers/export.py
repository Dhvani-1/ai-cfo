import os
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.transaction import Transaction
from models.invoice import Invoice
from auth.dependencies import get_current_user
from reports.pdf_report import generate_pdf_report
from reports.excel_report import generate_excel_report

router = APIRouter()

@router.get("/export-pdf")
def export_pdf(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Fetch transactions and invoices scoped to current authenticated user
        transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
        invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).all()
        
        # Generate the PDF report
        file_path = generate_pdf_report(current_user, transactions, invoices)
        
        # Verify file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Failed to generate PDF report")
            
        # Extract filename to send back in FileResponse
        filename = os.path.basename(file_path)
        
        # Add background task to delete the temporary file after it's served
        background_tasks.add_task(os.remove, file_path)
        
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.get("/export-excel")
def export_excel(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Fetch transactions and invoices scoped to current authenticated user
        transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
        invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).all()
        
        # Generate the Excel report
        file_path = generate_excel_report(current_user, transactions, invoices)
        
        # Verify file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Failed to generate Excel report")
            
        # Extract filename to send back in FileResponse
        filename = os.path.basename(file_path)
        
        # Add background task to delete the temporary file after it's served
        background_tasks.add_task(os.remove, file_path)
        
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel generation failed: {str(e)}")

@router.get("/report-summary")
def report_summary(current_user: User = Depends(get_current_user)):
    return {
        "available_reports": [
            "pdf",
            "excel"
        ]
    }
