from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_current_user 
from app.models import User, UserCreate, UserRead
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/me", response_model=UserRead)         # ← नवीन endpoint (2)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user