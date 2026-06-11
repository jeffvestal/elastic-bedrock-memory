"""
REFERENCE — what a no-memory ("amnesiac") Kiro actually produces for refunds.

The surprise from live testing: with the codebase in front of it, a capable agent gets
the *code patterns* right just by reading them — integer cents, Stripe idempotency +
backoff, JWT + ownership, a Refund model, async session. So "it reintroduces the float
bug / forgets auth" does NOT happen reliably.

What it CANNOT know lives in team decisions, not in code — and that's the honest contrast:
  GAP 1 — No amount cap. Only guards `amount <= 0`, so a caller can refund MORE than the
          order was, and repeatedly. The cap (original minus prior refunds) is policy, in memory only.
  GAP 2 — No refund window. The 90-day rule is policy, in memory only.
  GAP 3 — Amount-based idempotency key: f"{order_id}-refund-{amount_cents}". Two separate
          partial refunds of the SAME amount collide on one key → Stripe dedupes the second
          → the customer never gets it. The agent even rationalizes it in a comment. Wrong,
          and stated with confidence. (The fix — per-attempt UUID keys — is the Act 2 write beat.)
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import User, get_current_user
from ..db import get_session
from ..money import dollars_to_cents
from ..models import Order, Refund
from .. import payments

router = APIRouter()


class RefundRequest(BaseModel):
    amount: str  # decimal dollar string — CORRECT (cents at the boundary, no float)


@router.post("/orders/{order_id}/refund")
async def refund_order(
    order_id: str,
    body: RefundRequest,
    user: User = Depends(get_current_user),        # auth: CORRECT — copied from checkout.py
    session: AsyncSession = Depends(get_session),  # async session: CORRECT
) -> dict:
    order = await session.get(Order, order_id)
    if order is None or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.stripe_payment_intent_id is None:
        raise HTTPException(status_code=400, detail="Order has no payment to refund")

    amount_cents = dollars_to_cents(body.amount)   # cents: CORRECT
    if amount_cents <= 0:                          # GAP 1: only guards <= 0 — no cap against
        raise HTTPException(status_code=400, detail="Refund amount must be positive")
        #                                            the order total or prior refunds.
    # GAP 2: no 90-day window check anywhere.

    # GAP 3: amount-based key — two equal partial refunds on one order collide.
    idempotency_key = f"{order_id}-refund-{amount_cents}"
    stripe_refund = payments.create_refund(
        payment_intent_id=order.stripe_payment_intent_id,
        amount_cents=amount_cents,
        idempotency_key=idempotency_key,
    )
    session.add(
        Refund(
            id=str(uuid.uuid4()),
            order_id=order_id,
            amount_cents=amount_cents,
            stripe_refund_id=stripe_refund.id,
            idempotency_key=idempotency_key,
        )
    )
    return {"order_id": order_id, "refund_id": stripe_refund.id, "amount_cents": amount_cents}
