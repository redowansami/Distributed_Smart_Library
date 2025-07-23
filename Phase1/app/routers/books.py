from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas
from app.database import get_db
from app.crud import books as book_crud

router = APIRouter(prefix="/api/books", tags=["Books"])

@router.post("/", response_model=schemas.BookRead, status_code=201)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return book_crud.create_book(db, book)

@router.get("/", response_model=List[schemas.BookRead])
def search_books(search: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return book_crud.search_books(db, search)

@router.get("/{book_id}", response_model=schemas.BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = book_crud.get_book_by_id(db, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.put("/{book_id}", response_model=schemas.BookRead)
def update_book_route(
    book_id: int,
    book_data: schemas.BookUpdate,
    db: Session = Depends(get_db)
):
    updated_book = book_crud.update_book(db, book_id, book_data)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    success = book_crud.delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return
