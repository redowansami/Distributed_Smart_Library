from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models, schemas
from app.crud.books import update_book_availability_on_return

def create_loan(db: Session, loan_data: schemas.LoanCreate):
    loan = models.Loan(
        user_id=loan_data.user_id,
        book_id=loan_data.book_id,
        issue_date=datetime.now(datetime.timezone.utc),
        due_date=loan_data.due_date,
        status="ACTIVE",
        extensions_count=0
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan

def return_loan(db: Session, loan_id: int):
    loan = db.query(models.Loan).filter(
        models.Loan.id == loan_id,
        models.Loan.status != "RETURNED"
    ).first()
    if not loan:
        return None

    loan.return_date = datetime.now(datetime.timezone.utc)
    loan.status = "RETURNED"

    update_book_availability_on_return(db, loan.book_id)

    db.commit()
    db.refresh(loan)
    return loan

def get_loan_history(db: Session, user_id: int):
    return db.query(models.Loan).filter(models.Loan.user_id == user_id).all()

def get_overdue_loans(db: Session):
    now = datetime.now(datetime.timezone.utc)
    overdue_loans = db.query(models.Loan).filter(
        models.Loan.due_date < now,
        models.Loan.status == "ACTIVE"
    ).all()

    results = []
    for loan in overdue_loans:
        days_overdue = (now - loan.due_date).days
        results.append({
            "id": loan.id,
            "user": loan.user,
            "book": loan.book,
            "issue_date": loan.issue_date,
            "due_date": loan.due_date,
            "days_overdue": days_overdue
        })
    return results

def extend_loan_due_date(db: Session, loan_id: int, days: int):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if loan:
        original_due = loan.due_date
        loan.due_date += timedelta(days=days)
        loan.extensions_count += 1
        db.commit()
        db.refresh(loan)
        return {
            "id": loan.id,
            "user_id": loan.user_id,
            "book_id": loan.book_id,
            "issue_date": loan.issue_date,
            "original_due_date": original_due,
            "extended_due_date": loan.due_date,
            "status": loan.status,
            "extensions_count": loan.extensions_count
        }
    return None