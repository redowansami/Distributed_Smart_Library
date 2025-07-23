from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routers import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Loan Service")

app.include_router(router)