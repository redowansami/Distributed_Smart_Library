from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app import models, schemas
from fastapi import HTTPException

def create_book(db: Session, book: schemas.BookCreate):
    existing_book = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if existing_book:
        raise HTTPException(status_code=400, detail="ISBN already exists")
    db_book = models.Book(
        **book.model_dump(),
        available_copies=book.copies
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_book_by_id(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def search_books(db: Session, search: str = None, page: int = 1, per_page: int = 10):
    query = db.query(models.Book)
    if search:
        query = query.filter(
            or_(
                models.Book.title.ilike(f"%{search}%"),
                models.Book.author.ilike(f"%{search}%"),
                models.Book.isbn.ilike(f"%{search}%")
            )
        )
    total = query.count()
    books = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"books": books, "total": total, "page": page, "per_page": per_page}

def update_book(db: Session, book_id: int, book_data: schemas.BookUpdate):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        return None
    for key, value in book_data.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    db_book.updated_at = func.now()
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book_availability(db: Session, book_id: int, availability_data: schemas.BookAvailabilityUpdate):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        return None
    if availability_data.operation == "increment":
        db_book.available_copies += availability_data.available_copies
    elif availability_data.operation == "decrement":
        if db_book.available_copies < availability_data.available_copies:
            raise HTTPException(status_code=400, detail="Not enough available copies")
        db_book.available_copies -= availability_data.available_copies
    else:
        raise HTTPException(status_code=400, detail="Invalid operation")
    db_book.updated_at = func.now()
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        return False
    db.delete(db_book)
    db.commit()
    return True