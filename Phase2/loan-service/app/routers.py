from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
import httpx

router = APIRouter(prefix="/api/loans", tags=["Loans"])

@router.post("/", response_model=schemas.Loan, status_code=201)
async def issue_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    try:
        return await crud.create_loan(db, loan)
    except HTTPException as e:
        raise e
    except Exception as ex:
        print(f"Unexpected error in issue_loan: {ex}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/returns/", response_model=schemas.Loan)
async def return_book(return_data: schemas.LoanReturn, db: Session = Depends(get_db)):
    try:
        return await crud.return_loan(db, return_data.loan_id)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}", response_model=schemas.UserLoanHistory)
async def get_user_loans(user_id: int, db: Session = Depends(get_db)):
    try:
        return await crud.get_loan_history_details(db, user_id)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{loan_id}", response_model=schemas.LoanDetails)
async def get_loan(loan_id: int, db: Session = Depends(get_db)):
    try:
        return await crud.get_loan_details(db, loan_id)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{loan_id}/extend", response_model=schemas.LoanExtensionResponse)
def extend_loan(loan_id: int, extension: schemas.LoanExtensionRequest, db: Session = Depends(get_db)):
    try:
        updated_loan = crud.extend_loan_due_date(db, loan_id, extension.extension_days)
        if not updated_loan:
            raise HTTPException(status_code=400, detail="Extension failed")
        return updated_loan
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")