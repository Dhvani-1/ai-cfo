import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI
from routers import upload
from routers import transactions
from routers import dashboard
from routers import chat
from routers import insights
from routers import forecast
from routers import health
from routers import invoice
from routers import fraud
from routers import tax
from routers import auth
from routers import export
from database import engine, Base, SessionLocal
from models.user import User  # ensures model is registered
from models.transaction import Transaction  # ensures model is registered
from models.invoice import Invoice  # ensures model is registered
from services.categorizer import categorize

# Create database tables
Base.metadata.create_all(bind=engine)

def backfill_categories():
    db = SessionLocal()
    try:
        from sqlalchemy import or_
        uncategorized_txs = db.query(Transaction).filter(
            or_(
                Transaction.category == "Uncategorized",
                Transaction.category.is_(None),
                Transaction.category == ""
            )
        ).all()
        if uncategorized_txs:
            for tx in uncategorized_txs:
                desc = tx.description or ""
                tx.category = categorize(desc)
            db.commit()
            print(f"Successfully backfilled {len(uncategorized_txs)} transactions.")
    except Exception as e:
        print(f"Error backfilling categories: {e}")
        db.rollback()
    finally:
        db.close()

backfill_categories()

# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/invoices", exist_ok=True)
os.makedirs("exports", exist_ok=True)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)
app.include_router(chat.router)
app.include_router(insights.router)
app.include_router(forecast.router)
app.include_router(health.router)
app.include_router(invoice.router)
app.include_router(fraud.router)
app.include_router(tax.router)
app.include_router(auth.router)
app.include_router(export.router)