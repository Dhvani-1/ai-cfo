from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    vendor = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    invoice_date = Column(Date, nullable=True)
    total_amount = Column(Float, nullable=True)
    gst_number = Column(String, nullable=True)
    category = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    ocr_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

