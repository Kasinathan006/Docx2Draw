"""
Stripe webhook endpoint (guide §7.2).

Handles subscription lifecycle events. When Stripe is not configured the route
returns HTTP 503 instead of crashing, so the app boots without Stripe keys.
"""
from fastapi import APIRouter, Header, Request

from ....config import settings
from ....core.exceptions import Doc2DrawError
from ....services.billing_service import update_user_subscription

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class StripeNotConfigured(Doc2DrawError):
    status_code = 503
    detail = "Stripe is not configured on this server"


class WebhookError(Doc2DrawError):
    status_code = 400
    detail = "Invalid webhook payload"


@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(default=None)):
    if not settings.stripe_enabled:
        raise StripeNotConfigured()

    import stripe

    stripe.api_key = settings.stripe_secret_key
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except ValueError as exc:
        raise WebhookError(f"Invalid payload: {exc}") from exc
    except stripe.error.SignatureVerificationError as exc:  # type: ignore[attr-defined]
        raise WebhookError(f"Invalid signature: {exc}") from exc

    event_type = event["type"]
    data_object = event["data"]["object"]

    if event_type == "checkout.session.completed":
        await update_user_subscription(
            user_id=data_object.get("client_reference_id"),
            stripe_customer_id=data_object.get("customer"),
            tier="pro",
            status="active",
        )
    elif event_type in ("customer.subscription.deleted", "customer.subscription.updated"):
        status = data_object.get("status")
        await update_user_subscription(
            stripe_customer_id=data_object.get("customer"),
            tier="pro" if status == "active" else "free",
            status=status or "canceled",
        )

    return {"status": "success"}
