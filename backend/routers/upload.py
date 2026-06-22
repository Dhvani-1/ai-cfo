from fastapi import APIRouter, UploadFile, File, Depends
import shutil
from sqlalchemy.orm import Session

from database import get_db
from models.transaction import Transaction
from models.user import User
from auth.dependencies import get_current_user
from services.parser import parse_file
from services.categorizer import categorize

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):

    # Save file
    path = f"uploads/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse records
    records = parse_file(path)

    # Store records
    for row in records:

        desc = row["Description"] or ""
        transaction = Transaction(
            date=row["Date"],
            description=row["Description"],
            amount=row["Amount"],
            category=categorize(desc),
            type="Income" if row["Amount"] >= 0 else "Expense",
            user_id=current_user.id
        )

        db.add(transaction)

    db.commit()

    return {
        "message": "Uploaded and stored successfully"
    }