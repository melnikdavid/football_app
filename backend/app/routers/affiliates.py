from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.affiliate import Affiliate, Referral
from app.schemas.affiliate import AffiliateStatsOut
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/affiliates", tags=["affiliates"])


@router.get("/me/stats", response_model=AffiliateStatsOut)
async def get_affiliate_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Affiliate).where(Affiliate.user_id == current_user.id))
    affiliate = result.scalar_one_or_none()
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate account not found")

    total_refs = await db.execute(
        select(func.count()).where(Referral.affiliate_id == affiliate.id)
    )
    converted_refs = await db.execute(
        select(func.count()).where(
            Referral.affiliate_id == affiliate.id,
            Referral.converted_at.isnot(None),
        )
    )

    return AffiliateStatsOut(
        id=affiliate.id,
        code=affiliate.code,
        commission_pct=affiliate.commission_pct,
        total_earned=affiliate.total_earned,
        total_referrals=total_refs.scalar() or 0,
        converted_referrals=converted_refs.scalar() or 0,
    )
