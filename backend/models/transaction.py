from sqlalchemy import Column,Integer,String,Float,Date,ForeignKey
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    description = Column(String)
    amount = Column(Float)
    category = Column(String)
    type = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)