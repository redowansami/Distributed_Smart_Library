from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app import models, schemas
from fastapi import HTTPException
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

USER_SERVICE_URL = "http://0.0.0.0:8081"
BOOK_SERVICE_URL = "http://0.0.0.0:8082"

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), retry=retry_if_exception_type(httpx.RequestError))
async def get_user(client: httpx.AsyncClient, user_id: int):
    try:
        response = await client.get(f"{USER_SERVICE_URL}/api/users/{user_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(status_code=503, detail="User Service unavailable")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="User Service unavailable")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), retry=retry_if_exception_type(httpx.RequestError))
async def get_book(client: httpx.AsyncClient, book_id: int):
    try:
        response = await client.get(f"{BOOK_SERVICE_URL}/api/books/{book_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Book not found")
        raise HTTPException(status_code=503, detail="Book Service unavailable")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Book Service unavailable")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), retry=retry_if_exception_type(httpx.RequestError))
async def update_book_availability(client: httpx.AsyncClient, book_id: int, operation: str, copies: int = 1):
    try:
        response = await client.patch(
            f"{BOOK_SERVICE_URL}/api/books/{book_id}/availability",
            json={"available_copies": copies, "operation": operation}
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Book not found")
        if e.response.status_code == 400:
            raise HTTPException(status_code=400, detail="Not enough available copies")
        raise HTTPException(status_code=503, detail="Book Service unavailable")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Book Service unavailable")

async def create_loan(db: Session, loan_data: schemas.LoanCreate):
    async with httpx.AsyncClient(timeout=5.0) as client:

        await get_user(client, loan_data.user_id)

        book = await get_book(client, loan_data.book_id)
        if book["available_copies"] < 1:
            raise HTTPException(status_code=400, detail="Book not available")

        await update_book_availability(client, loan_data.book_id, "decrement")

        loan = models.Loan(
            user_id=loan_data.user_id,
            book_id=loan_data.book_id,
            issue_date=datetime.now(timezone.utc),
            due_date=loan_data.due_date,
            status="ACTIVE",
            extensions_count=0
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan

async def return_loan(db: Session, loan_id: int):
    loan = db.query(models.Loan).filter(
        models.Loan.id == loan_id,
        models.Loan.status != "RETURNED"
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found or already returned")
    async with httpx.AsyncClient(timeout=5.0) as client:
        
        await update_book_availability(client, loan.book_id, "increment")
        
        loan.return_date = datetime.now(timezone.utc)
        loan.status = "RETURNED"
        db.commit()
        db.refresh(loan)
        return loan

def get_loan_by_id(db: Session, loan_id: int):
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()

async def get_loan_details(db: Session, loan_id: int):
    loan = get_loan_by_id(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    async with httpx.AsyncClient(timeout=5.0) as client:
        user = await get_user(client, loan.user_id)
        book = await get_book(client, loan.book_id)
        return {
            "id": loan.id,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            },
            "book": {
                "id": book["id"],
                "title": book["title"],
                "author": book["author"]
            },
            "issue_date": loan.issue_date,
            "due_date": loan.due_date,
            "return_date": loan.return_date,
            "status": loan.status
        }

def get_loan_history(db: Session, user_id: int):
    return db.query(models.Loan).filter(models.Loan.user_id == user_id).all()

async def get_loan_history_details(db: Session, user_id: int):
    loans = get_loan_history(db, user_id)
    async with httpx.AsyncClient(timeout=5.0) as client:
        results = []
        for loan in loans:
            book = await get_book(client, loan.book_id)
            results.append({
                "id": loan.id,
                "book": {
                    "id": book["id"],
                    "title": book["title"],
                    "author": book["author"]
                },
                "issue_date": loan.issue_date,
                "due_date": loan.due_date,
                "return_date": loan.return_date,
                "status": loan.status
            })
        return {"loans": results, "total": len(results)}

def extend_loan_due_date(db: Session, loan_id: int, days: int):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Cannot extend a returned loan")
    if loan.extensions_count >= 2:
        raise HTTPException(status_code=400, detail="Maximum extensions reached")
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