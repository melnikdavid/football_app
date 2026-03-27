from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.challenge import UserPoints
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse
from app.middleware.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user,
)
from app.workers.notification_tasks import send_welcome_sequence

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    await db.flush()  # get user.id

    profile = Profile(user_id=user.id, full_name=body.full_name)
    db.add(profile)

    points = UserPoints(user_id=user.id)
    db.add(points)

    # Handle affiliate referral
    if body.ref_code:
        from app.models.affiliate import Affiliate, Referral
        result = await db.execute(select(Affiliate).where(Affiliate.code == body.ref_code))
        affiliate = result.scalar_one_or_none()
        if affiliate:
            referral = Referral(affiliate_id=affiliate.id, referred_user_id=user.id)
            db.add(referral)

    await db.commit()

    send_welcome_sequence.delay(str(user.id), user.email, body.full_name)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    user_id = decode_token(body.refresh_token, expected_type="refresh")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: User = Depends(get_current_user)):
    # JWT is stateless; client should discard tokens.
    # For token invalidation, maintain a Redis blocklist here if needed.
    return None
