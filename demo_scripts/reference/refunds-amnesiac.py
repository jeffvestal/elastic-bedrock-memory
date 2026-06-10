"""
REFERENCE — the AMNESIAC (wrong) refund implementation (Act 1).

This is the kind of plausible-but-wrong code a Kiro with no access to the team's
decision history produces. Use it to confirm a take captured the right slips, or as a
paste-in if a live run behaves "too well." Each slip is annotated.

DO NOT ship this. It is wrong on purpose.

Slips:
  1. float money  → reintroduces the 1-cent bug          (violates sess-005)
  2. Stripe Refund with NO idempotency key, no backoff    (violates sess-004 / sess-007)
  3. route has NO auth dependency                         (violates sess-002)
  4. no guard against double-refund / over-refund         (violates sess-004 pattern)
"""

import stripe
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RefundRequest(BaseModel):
    amount: float   # SLIP 1: float dollars for money


# SLIP 3: no `Depends(get_current_user)` — anyone can hit this and refund money.
@router.post("/orders/{order_id}/refund")
async def refund_order(order_id: str, body: RefundRequest):
    order = get_order(order_id)  # (sync-ish ad-hoc access; ignores the async session)

    # SLIP 1 (cont.): float math on money → 14.989999999999998 territory.
    amount_dollars = body.amount
    amount_cents = int(amount_dollars * 100)

    # SLIP 4: no check that the order is paid, no prior-refund tally, no cap,
    #         no refund window — a caller can refund repeatedly or over the total.

    # SLIP 2: Stripe refund with no idempotency key and no retry/backoff — a retry
    #         issues a SECOND refund.
    refund = stripe.Refund.create(
        payment_intent=order.stripe_payment_intent_id,
        amount=amount_cents,
    )

    return {"refund_id": refund.id, "amount": amount_dollars, "status": "refunded"}
