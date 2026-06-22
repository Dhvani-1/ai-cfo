from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.transaction import Transaction
from models.user import User
from auth.dependencies import get_current_user
from ai.rag_chain import ask_question
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    result = ask_question(request.question, transactions)
    return result
