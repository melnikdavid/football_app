import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.challenge import Challenge, ChallengeCompletion, UserPoints, UserRank
from app.schemas.challenge import ChallengeOut, ChallengeCompleteIn, UserPointsOut
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/challenges", tags=["challenges"])

RANK_THRESHOLDS = {
    UserRank.bronze: 0,
    UserRank.silver: 100,
    UserRank.gold: 300,
    UserRank.champion: 700,
}


def _calculate_rank(points: int) -> UserRank:
    rank = UserRank.bronze
    for r, threshold in RANK_THRESHOLDS.items():
        if points >= threshold:
            rank = r
    return rank


@router.get("", response_model=list[ChallengeOut])
async def list_challenges(
    status: str | None = Query(None, description="active | upcoming | past"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    q = select(Challenge)
    if status == "active":
        q = q.where(Challenge.start_date <= today, Challenge.end_date >= today)
    elif status == "upcoming":
        q = q.where(Challenge.start_date > today)
    elif status == "past":
        q = q.where(Challenge.end_date < today)
    result = await db.execute(q.order_by(Challenge.start_date.desc()))
    return result.scalars().all()


@router.post("/{challenge_id}/complete", response_model=UserPointsOut)
async def complete_challenge(
    challenge_id: uuid.UUID,
    body: ChallengeCompleteIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Challenge).where(Challenge.id == challenge_id))
    challenge = result.scalar_one_or_none()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Check not already completed
    existing = await db.execute(
        select(ChallengeCompletion).where(
            ChallengeCompletion.user_id == current_user.id,
            ChallengeCompletion.challenge_id == challenge_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Challenge already completed")

    completion = ChallengeCompletion(
        user_id=current_user.id,
        challenge_id=challenge_id,
        evidence_url=body.evidence_url,
    )
    db.add(completion)

    result = await db.execute(select(UserPoints).where(UserPoints.user_id == current_user.id))
    user_points = result.scalar_one_or_none()
    if not user_points:
        user_points = UserPoints(user_id=current_user.id, total_points=0)
        db.add(user_points)

    user_points.total_points += challenge.points
    user_points.rank = _calculate_rank(user_points.total_points)

    await db.commit()
    await db.refresh(user_points)
    return user_points
