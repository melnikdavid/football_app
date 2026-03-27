import stripe
from app.config import get_settings

settings = get_settings()


def get_stripe_client() -> stripe.StripeClient:
    return stripe.StripeClient(settings.stripe_secret_key)


async def create_stripe_trial_subscription(customer_email: str, payment_method_token: str) -> dict:
    client = get_stripe_client()

    customer = client.customers.create(params={"email": customer_email})
    client.payment_methods.attach(
        payment_method_token,
        params={"customer": customer.id},
    )
    client.customers.update(
        customer.id,
        params={"invoice_settings": {"default_payment_method": payment_method_token}},
    )

    subscription = client.subscriptions.create(params={
        "customer": customer.id,
        "items": [{"price": "price_monthly_269_ils"}],  # configure in Stripe dashboard
        "trial_period_days": 7,
        "trial_settings": {"end_behavior": {"missing_payment_method": "cancel"}},
    })

    return {
        "provider_customer_id": customer.id,
        "provider_subscription_id": subscription.id,
        "trial_end": subscription.trial_end,
        "status": subscription.status,
    }


async def cancel_stripe_subscription(subscription_id: str) -> bool:
    client = get_stripe_client()
    client.subscriptions.cancel(subscription_id)
    return True


def verify_stripe_webhook(payload: bytes, sig_header: str) -> dict:
    return stripe.WebhookSignature.verify_header(
        payload.decode(),
        sig_header,
        settings.stripe_webhook_secret,
    )
