from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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
    extensions_count: int

    class Config:
        orm_mode = True

class UserLoanRecord(BaseModel):
    id: int
    book: BookInfo
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str

    class Config:
        orm_mode = True


class UserLoanHistory(BaseModel):
    loans: List[UserLoanRecord]
    total: int

    class Config:
        orm_mode = True


class LoanDetails(BaseModel):
    id: int
    user: UserInfo
    book: BookInfo
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str

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