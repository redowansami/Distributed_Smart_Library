from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    student = "student"
    faculty = "faculty"

class LoanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: RoleEnum

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum

    class Config:
        orm_mode = True

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
    updated_at: datetime

    class Config:
        orm_mode = True

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    copies: Optional[int] = None
    available_copies: Optional[int] = None

class LoanCreate(BaseModel):
    user_id: int
    book_id: int
    due_date: datetime

class LoanReturn(BaseModel):
    loan_id: int

class BookInfo(BaseModel):
    id: int
    title: str
    author: str

class UserInfo(BaseModel):
    id: int
    name: str
    email: str

class Loan(BaseModel):
    id: int
    user_id: int
    book_id: int
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str

    class Config:
        orm_mode = True

class UserLoanHistory(BaseModel):
    id: int
    book: BookInfo
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str

    class Config:
        orm_mode = True

class OverdueLoan(BaseModel):
    id: int
    user: UserInfo
    book: BookInfo
    issue_date: datetime
    due_date: datetime
    days_overdue: int

    class Config:
        orm_mode = True

class LoanExtensionRequest(BaseModel):
    extension_days: int

class LoanExtensionResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    issue_date: datetime
    original_due_date: datetime
    extended_due_date: datetime
    status: str
    extensions_count: int

class PopularBook(BaseModel):
    book_id: int
    title: str
    author: str
    borrow_count: int

class ActiveUser(BaseModel):
    user_id: int
    name: str
    books_borrowed: int
    current_borrows: int

class OverviewStats(BaseModel):
    total_books: int
    total_users: int
    books_available: int
    books_borrowed: int
    overdue_loans: int
    loans_today: int
    returns_today: int