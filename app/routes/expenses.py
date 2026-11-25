from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from app.database import get_session
from app.dependencies import get_current_user
from app.models import Expense, ExpenseCreate, ExpenseRead, ExpenseUpdate, User
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select
from app.database import get_session
from app.dependencies import get_current_user
from app.models import (
    CategoryTotal,
    Expense,
    ExpenseCreate,
    ExpenseRead,
    ExpenseUpdate,
    MonthlySummary,
    User,
)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def get_own_expense(expense_id: int, session: Session, user: User) -> Expense:
    expense = session.get(Expense, expense_id)
    if not expense or expense.user_id != user.id:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    data: ExpenseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    expense = Expense(**data.model_dump(), user_id=current_user.id)
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense


@router.get("", response_model=List[ExpenseRead])
def list_expenses(
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = select(Expense).where(Expense.user_id == current_user.id)
    if category:
        query = query.where(Expense.category == category)
    query = query.order_by(Expense.spent_on.desc()).offset(skip).limit(limit)
    return session.exec(query).all()


@router.get("/summary", response_model=MonthlySummary)
def monthly_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    query = (
        select(
            Expense.category,
            func.sum(Expense.amount),
            func.count(Expense.id),
        )
        .where(
            Expense.user_id == current_user.id,
            Expense.spent_on >= start,
            Expense.spent_on < end,
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    )
    rows = session.exec(query).all()

    by_category = [
        CategoryTotal(category=cat, total=float(total), count=cnt)
        for cat, total, cnt in rows
    ]
    return MonthlySummary(
        year=year,
        month=month,
        total=sum(c.total for c in by_category),
        count=sum(c.count for c in by_category),
        by_category=by_category,
    )    

@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(
    expense_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return get_own_expense(expense_id, session, current_user)


@router.put("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    expense = get_own_expense(expense_id, session, current_user)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(expense, key, value)
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    expense = get_own_expense(expense_id, session, current_user)
    session.delete(expense)
    session.commit()

