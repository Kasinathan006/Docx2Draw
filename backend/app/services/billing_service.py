"""
Billing service (guide §5.1 services/billing_service.py).

Manages subscription tiers and monthly upload quotas. When neither Supabase nor
a database is configured, quota checks always pass and subscription updates are
logged no-ops, so the API is fully usable without Stripe.
"""
import logging
from typing import Optional

from ..config import settings

logger = logging.getLogger("doc2draw.billing")

# Monthly diagram quota per tier (None == unlimited).
TIER_QUOTAS = {"free": 3, "pro": None, "team": None}
# Max upload size (MB) per tier.
TIER_MAX_UPLOAD_MB = {"free": 50, "pro": 500, "team": 500}


def quota_for_tier(tier: str) -> Optional[int]:
    return TIER_QUOTAS.get(tier, TIER_QUOTAS["free"])


def check_quota(tier: str, used_this_month: int) -> bool:
    """Return True if a new generation is permitted for this tier."""
    limit = quota_for_tier(tier)
    if limit is None:
        return True
    return used_this_month < limit


async def update_user_subscription(
    user_id: Optional[str] = None,
    stripe_customer_id: Optional[str] = None,
    tier: str = "free",
    status: str = "active",
) -> None:
    """
    Update a user's subscription tier/status.

    Persists to Supabase when configured; otherwise logs the change so local
    development never fails on a missing database.
    """
    if not settings.supabase_enabled:
        logger.info(
            "Subscription update (no DB): user=%s customer=%s tier=%s status=%s",
            user_id, stripe_customer_id, tier, status,
        )
        return

    try:  # pragma: no cover - requires live Supabase
        from supabase import create_client

        client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        patch = {"subscription_tier": tier, "subscription_status": status}
        if stripe_customer_id:
            patch["stripe_customer_id"] = stripe_customer_id
        query = client.table("profiles").update(patch)
        if user_id:
            query = query.eq("id", user_id)
        else:
            query = query.eq("stripe_customer_id", stripe_customer_id)
        query.execute()
    except Exception as exc:
        logger.error("Failed to update subscription in Supabase: %s", exc)
