import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.content import Content, ContentView, ContentType
from app.models.subscription import Subscription, SubscriptionStatus
from app.schemas.content import ContentOut, ContentViewIn
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/content", tags=["content"])


async def _require_active_subscription(user: User, db: AsyncSession):
    result = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
    sub = result.scalar_one_or_none()
    if not sub or sub.status not in (SubscriptionStatus.active, SubscriptionStatus.trialing):
        raise HTTPException(status_code=403, detail="Active subscription required")


@router.get("", response_model=list[ContentOut])
async def list_content(
    type: ContentType | None = Query(None),
    category: str | None = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_active_subscription(current_user, db)

    q = select(Content).where(Content.published_at.isnot(None))
    if type:
        q = q.where(Content.type == type)
    if category:
        q = q.where(Content.topic_category == category)
    q = q.order_by(Content.published_at.desc()).limit(limit).offset(offset)

    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{content_id}", response_model=ContentOut)
async def get_content(
    content_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if not content.is_free:
        await _require_active_subscription(current_user, db)

    return content


@router.post("/{content_id}/view", status_code=204)
async def record_view(
    content_id: uuid.UUID,
    body: ContentViewIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Content).where(Content.id == content_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Content not found")

    view = ContentView(
        user_id=current_user.id,
        content_id=content_id,
        completion_pct=body.completion_pct,
    )
    db.add(view)
    await db.commit()
