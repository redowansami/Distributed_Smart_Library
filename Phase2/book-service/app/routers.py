from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app import schemas, crud
from app.database import get_db

router = APIRouter(prefix="/api/books", tags=["Books"])

@router.post("/", response_model=schemas.BookRead, status_code=201)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_book(db, book)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=schemas.BookSearchResponse)
def search_books(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return crud.search_books(db, search, page, per_page)

@router.get("/{book_id}", response_model=schemas.BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book_by_id(db, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.put("/{book_id}", response_model=schemas.BookRead)
def update_book(book_id: int, book_data: schemas.BookUpdate, db: Session = Depends(get_db)):
    updated_book = crud.update_book(db, book_id, book_data)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@router.patch("/{book_id}/availability", response_model=schemas.BookRead)
def update_availability(book_id: int, availability_data: schemas.BookAvailabilityUpdate, db: Session = Depends(get_db)):
    updated_book = crud.update_book_availability(db, book_id, availability_data)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    success = crud.delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return