import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, SQLModel, select
from app.database import get_session
from app.models import User
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)

router = APIRouter(tags=["Auth"])


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(SQLModel):
    refresh_token: str


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == form.username)).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=Token)
def refresh(body: RefreshRequest, session: Session = Depends(get_session)):
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        user_id = decode_token(body.refresh_token, "refresh")
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise error

    if not session.get(User, user_id):
        raise error

    return Token(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )