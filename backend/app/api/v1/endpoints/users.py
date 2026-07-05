"""
User profile & usage-quota endpoints (guide §5.1 endpoints/users.py).

Works anonymously when auth is disabled, returning a default free-tier profile.
"""
from fastapi import APIRouter, Depends

from ....core.auth import CurrentUser, get_current_user
from ....services.billing_service import quota_for_tier
from ....models.schemas import UserProfileResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
def get_me(user: CurrentUser = Depends(get_current_user)):
    tier = "free"
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        subscription_tier=tier,
        subscription_status="active",
        monthly_upload_count=0,
        monthly_quota=quota_for_tier(tier) or 0,
        authenticated=user.authenticated,
    )
