from datetime import date
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class UserCreate(SQLModel):
    name: str = Field(max_length=100)
    email: str = Field(max_length=255)
    password: str = Field(min_length=6)


class UserRead(SQLModel):
    id: int
    name: str
    email: str


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)

    expenses: List["Expense"] = Relationship(back_populates="user")


class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    amount: float
    category: str = Field(max_length=50)
    spent_on: date
    note: Optional[str] = Field(default=None, max_length=500)

    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="expenses")

class ExpenseCreate(SQLModel):
    title: str = Field(max_length=200)
    amount: float = Field(gt=0)
    category: str = Field(max_length=50)
    spent_on: date
    note: Optional[str] = Field(default=None, max_length=500)


class ExpenseUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=200)
    amount: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = Field(default=None, max_length=50)
    spent_on: Optional[date] = None
    note: Optional[str] = Field(default=None, max_length=500)


class ExpenseRead(SQLModel):
    id: int
    title: str
    amount: float
    category: str
    spent_on: date
    note: Optional[str] = None

class CategoryTotal(SQLModel):
    category: str
    total: float
    count: int


class MonthlySummary(SQLModel):
    year: int
    month: int
    total: float
    count: int
    by_category: List[CategoryTotal]    
    