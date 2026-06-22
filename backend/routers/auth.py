from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.transaction import Transaction
from models.invoice import Invoice
from auth.security import hash_password, verify_password, validate_password, create_access_token
from auth.dependencies import get_current_user
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter()

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # 1. Enforce password complexity rules
    if not validate_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet minimum requirements."
        )
    
    # 2. Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 3. Create user
    hashed = hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "created_at": new_user.created_at.isoformat() if new_user.created_at else None
    }

@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_payload = {
        "sub": user.email,
        "user_id": user.id
    }
    access_token = create_access_token(data=token_payload)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_minutes": 60
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    transaction_count = db.query(Transaction).filter(Transaction.user_id == current_user.id).count()
    invoice_count = db.query(Invoice).filter(Invoice.user_id == current_user.id).count()
    
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "statistics": {
            "transactions": transaction_count,
            "invoices": invoice_count
        }
    }

@router.post("/change-password")
def change_password(data: ChangePassword, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    if not validate_password(data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet minimum requirements."
        )
    
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"detail": "Password updated successfully"}
