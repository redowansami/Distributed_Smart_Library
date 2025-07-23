from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models, schemas
from datetime import datetime


from datetime import datetime

def create_book(db: Session, book: schemas.BookCreate):
    current_time = datetime.now(datetime.timezone.utc)
    db_book = models.Book(
        **book.model_dump(),
        available_copies=book.copies,
        created_at=current_time,
        updated_at=current_time
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book



def get_book_by_id(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def search_books(db: Session, search: str = None):
    if search:
        return db.query(models.Book).filter(
            or_(
                models.Book.title.ilike(f"%{search}%"),
                models.Book.author.ilike(f"%{search}%"),
                models.Book.isbn.ilike(f"%{search}%")
            )
        ).all()
    return db.query(models.Book).all()


def update_book(db: Session, book_id: int, book_data: schemas.BookUpdate):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        return None

    for key, value in book_data.model_dump(exclude_unset=True).items():
        setattr(db_book, key, value)

    db_book.updated_at = datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_copies(db: Session, book_id: int, delta: int):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book:
        book.available_copies += delta
        book.updated_at = datetime.now(datetime.timezone.utc)
        db.commit()
        db.refresh(book)
    return book


def delete_book(db: Session, book_id: int):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        return False
    db.delete(db_book)
    db.commit()
    return True

def update_book_availability_on_return(db: Session, book_id: int):

    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return None

    book.available_copies += 1
    book.updated_at = datetime.now(datetime.timezone.utc)
    db.add(book)
    return book