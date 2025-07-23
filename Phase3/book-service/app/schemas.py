from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    copies: int

class BookRead(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    copies: int
    available_copies: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    copies: Optional[int] = None
    available_copies: Optional[int] = None

class BookAvailabilityUpdate(BaseModel):
    available_copies: int
    operation: str 

class BookSearchResponse(BaseModel):
    books: List[BookRead]
    total: int
    page: int
    per_page: int