from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.ai_session import AISession
from app.models.profile import Profile
from app.schemas.ai_session import AIMessageIn, AISessionOut
from app.middleware.auth import get_current_user
from app.services.ai_service import get_ai_response

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/session", response_model=AISessionOut)
async def get_session(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AISession)
        .where(AISession.user_id == current_user.id)
        .order_by(AISession.updated_at.desc())
    )
    session = result.scalar_one_or_none()

    if not session:
        session = AISession(user_id=current_user.id, messages=[])
        db.add(session)
        await db.commit()
        await db.refresh(session)

    return session


@router.post("/message", response_model=AISessionOut)
async def send_message(
    body: AIMessageIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get or create session
    result = await db.execute(
        select(AISession)
        .where(AISession.user_id == current_user.id)
        .order_by(AISession.updated_at.desc())
    )
    session = result.scalar_one_or_none()
    if not session:
        session = AISession(user_id=current_user.id, messages=[])
        db.add(session)

    # Get user profile for context
    profile_result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = profile_result.scalar_one_or_none()
    profile_dict = None
    if profile:
        profile_dict = {
            "full_name": profile.full_name,
            "age": profile.age,
            "position": profile.position,
            "team": profile.team,
            "training_frequency": profile.training_frequency,
        }

    messages = list(session.messages)
    messages.append({"role": "user", "content": body.message})

    ai_reply = await get_ai_response(messages, profile_dict)
    messages.append({"role": "assistant", "content": ai_reply})

    # Keep last 50 messages to avoid context overflow
    session.messages = messages[-50:]

    await db.commit()
    await db.refresh(session)
    return session
