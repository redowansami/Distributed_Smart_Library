from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class RoleEnum(enum.Enum):
    student = "student"
    faculty = "faculty"

class LoanStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)

    loans = relationship("Loan", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    loans = relationship("Loan", back_populates="book")

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime)
    return_date = Column(DateTime, nullable=True)
    status = Column(Enum(LoanStatus), default=LoanStatus.ACTIVE)
    extensions_count = Column(Integer, default=0)

    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")
