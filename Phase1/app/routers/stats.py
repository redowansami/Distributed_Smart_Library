from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, cast, Date
from datetime import date, datetime

from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/api/stats",
    tags=["stats"]
)

@router.get("/books/popular", response_model=list[schemas.PopularBook])
def get_most_borrowed_books(db: Session = Depends(get_db)):
    result = (
        db.query(
            models.Loan.book_id,
            models.Book.title,
            models.Book.author,
            func.count(models.Loan.id).label("borrow_count")
        )
        .join(models.Book, models.Loan.book_id == models.Book.id)
        .group_by(models.Loan.book_id, models.Book.title, models.Book.author)
        .order_by(func.count(models.Loan.id).desc())
        .limit(10)
        .all()
    )
    return result

@router.get("/users/active", response_model=List[schemas.ActiveUser])
def get_active_users(db: Session = Depends(get_db)):
    results = db.query(
        models.User.id.label("user_id"),
        models.User.name,
        func.count(models.Loan.id).label("books_borrowed"),
        func.sum(case((models.Loan.status == "ACTIVE", 1), else_=0)).label("current_borrows")
    ).join(models.Loan, models.User.id == models.Loan.user_id)\
     .group_by(models.User.id)\
     .order_by(func.count(models.Loan.id).desc())\
     .limit(10)\
     .all()

    return [
        {
            "user_id": row.user_id,
            "name": row.name,
            "books_borrowed": row.books_borrowed,
            "current_borrows": row.current_borrows
        }
        for row in results
    ]


@router.get("/overview", response_model=schemas.OverviewStats)
def get_overview_stats(db: Session = Depends(get_db)):
    total_books = db.query(func.sum(models.Book.copies)).scalar() or 0
    total_users = db.query(func.count(models.User.id)).scalar()
    books_available = db.query(func.sum(models.Book.available_copies)).scalar() or 0
    books_borrowed = db.query(func.count()).select_from(models.Loan).filter(models.Loan.status == "ACTIVE").scalar()
    overdue_loans = db.query(func.count()).select_from(models.Loan).filter(
        models.Loan.status == "ACTIVE",
        models.Loan.due_date < datetime.now(datetime.timezone.utc)
    ).scalar()
    today = date.today()
    loans_today = db.query(func.count()).select_from(models.Loan).filter(
        cast(models.Loan.issue_date, Date) == today
    ).scalar()
    returns_today = db.query(func.count()).select_from(models.Loan).filter(
        cast(models.Loan.return_date, Date) == today
    ).scalar()

    return {
        "total_books": total_books,
        "total_users": total_users,
        "books_available": books_available,
        "books_borrowed": books_borrowed,
        "overdue_loans": overdue_loans,
        "loans_today": loans_today,
        "returns_today": returns_today
    }
