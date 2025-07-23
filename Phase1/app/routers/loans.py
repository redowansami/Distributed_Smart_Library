from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app import models, schemas, crud
from app.crud import books as book_crud
from app.crud import loans as loan_crud
from app.database import get_db

router = APIRouter(prefix="/api/loans", tags=["loans"])

@router.post("/", response_model=schemas.Loan)
def issue_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    book = book_crud.get_book_by_id(db, loan.book_id)
    if not book or book.available_copies < 1:
        raise HTTPException(status_code=400, detail="Book not available")
    new_loan = loan_crud.create_loan(db, loan)
    book_crud.update_copies(db, loan.book_id, -1)
    return new_loan

@router.post("/returns/", response_model=schemas.Loan)
def return_book(return_data: schemas.LoanReturn, db: Session = Depends(get_db)):
    loan = loan_crud.return_loan(db, loan_id=return_data.loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found or already returned")
    return loan

@router.get("/overdue", response_model=List[schemas.OverdueLoan])
def get_overdue_loans(db: Session = Depends(get_db)):
    return loan_crud.get_overdue_loans(db)

@router.get("/{user_id}", response_model=List[schemas.UserLoanHistory])
def get_user_loans(user_id: int, db: Session = Depends(get_db)):
    return loan_crud.get_loan_history(db, user_id)

@router.put("/{loan_id}/extend", response_model=schemas.LoanExtensionResponse)
def extend_loan(loan_id: int, extension: schemas.LoanExtensionRequest, db: Session = Depends(get_db)):
    updated_loan = loan_crud.extend_loan_due_date(db, loan_id, extension.extension_days)
    if not updated_loan:
        raise HTTPException(status_code=400, detail="Extension failed")
    return updated_loan