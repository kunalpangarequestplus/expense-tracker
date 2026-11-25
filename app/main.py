from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app import models  # noqa: F401
from app.routes import users, auth, expenses


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Expense Tracker", lifespan=lifespan)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(expenses.router)


@app.get("/")
def home():
    return {"message": "Expense Tracker API चालू आहे"}