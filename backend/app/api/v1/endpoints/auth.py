from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings

router = APIRouter()

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 30


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=423,
            detail=f"Account locked until {user.locked_until.isoformat()}"
        )

    if not verify_password(data.password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
        await db.flush()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    await db.flush()

    token = create_access_token(subject=str(user.id))
    return Token(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user,
    )
