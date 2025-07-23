from fastapi import FastAPI
from app.routers import users, books, loans, stats
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Library System")

app.include_router(users.router)
app.include_router(books.router)
app.include_router(loans.router)
app.include_router(stats.router)
