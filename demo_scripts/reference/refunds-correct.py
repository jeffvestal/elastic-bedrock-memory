"""
REFERENCE — the CORRECT, policy-aware refund implementation (Act 2 target / fallback).

A memory-wired Kiro produces this after calling search-knowledge-facts. NOTE: a no-memory
Kiro also gets the *code patterns* right by reading the repo (cents, idempotency, JWT) —
see refunds-amnesiac.py. The real difference is the two policy rules and the idempotency-key
judgment below, none of which exist in the code.

From MEMORY (not in the code — this is what closes the gap):
  - Refund cap: partial refunds up to original charge minus prior refunds   (seeded policy, sess-004)
  - 90-day refund window; older -> HTTP 422 / manager approval               (seeded policy, sess-004)
  - Idempotency key is a per-attempt UUID (refund-{uuid}), NEVER amount-based (Act 2 write beat)

From reading the codebase (a no-memory agent gets these too):
  - integer cents, Stripe idempotency + backoff, JWT + ownership, async session, Refund ledger
"""

# ============================================================================
# app/models.py  — add the Refund ledger (mirrors the WebhookEvent idempotency idea)
# ============================================================================
from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

# class Refund(Base):
#     __tablename__ = "refunds"
#     id: Mapped[str] = mapped_column(String, primary_key=True)
#     order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
#     amount_cents: Mapped[int] = mapped_column(BigInteger)        # integer cents
#     stripe_refund_id: Mapped[str | None] = mapped_column(String, nullable=True)
#     idempotency_key: Mapped[str] = mapped_column(String, unique=True)  # stable per refund
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), server_default=func.now()
#     )


# ============================================================================
# app/payments.py  — add create_refund (same rules as create_charge)
# ============================================================================
import stripe

from .config import settings  # noqa: F401  (illustrative import path)

# def create_refund(*, payment_intent_id: str, amount_cents: int, idempotency_key: str):
#     """Refund (full or partial) against a PaymentIntent.
#
#     amount_cents is integer cents. idempotency_key is stable per refund record, so a
#     retry references the same key and Stripe never issues a second refund.
#     """
#     return _with_backoff(
#         lambda: stripe.Refund.create(
#             payment_intent=payment_intent_id,
#             amount=amount_cents,
#             idempotency_key=idempotency_key,
#         )
#     )


# ============================================================================
# app/routers/refunds.py  — the endpoint
# ============================================================================
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import User, get_current_user
from ..db import get_session
from ..money import dollars_to_cents
from ..models import Order  # and Refund, once added to models.py
from .. import payments

router = APIRouter()

REFUND_WINDOW_DAYS = 90  # NEW policy decision, saved to memory in Act 2


class RefundRequest(BaseModel):
    # Decimal string at the boundary — converted to integer cents, never float.
    amount: str


@router.post("/orders/{order_id}/refund")
async def refund_order(
    order_id: str,
    body: RefundRequest,
    user: User = Depends(get_current_user),          # sess-002: JWT on every route
    session: AsyncSession = Depends(get_session),    # sess-001: async session
) -> dict:
    order = await session.get(Order, order_id)
    if order is None or order.status != "paid":
        raise HTTPException(status_code=404, detail="No refundable order")

    # NEW policy: 90-day refund window.
    age = datetime.now(timezone.utc) - order.created_at
    if age > timedelta(days=REFUND_WINDOW_DAYS):
        raise HTTPException(status_code=422, detail="Order is outside the refund window")

    requested_cents = dollars_to_cents(body.amount)   # sess-005: integer cents
    if requested_cents <= 0:
        raise HTTPException(status_code=400, detail="Invalid refund amount")

    # sess-004 pattern: tally prior refunds; cap the partial at original minus prior.
    already_refunded = await session.scalar(
        select(func.coalesce(func.sum(Refund.amount_cents), 0)).where(  # noqa: F821
            Refund.order_id == order_id  # noqa: F821
        )
    )
    if requested_cents > order.amount_cents - already_refunded:
        raise HTTPException(status_code=422, detail="Refund exceeds remaining balance")

    refund_id = str(uuid.uuid4())
    stripe_refund = payments.create_refund(                # sess-004/007: idempotency + backoff
        payment_intent_id=order.stripe_payment_intent_id,
        amount_cents=requested_cents,
        idempotency_key=f"refund-{refund_id}",             # stable per refund record
    )

    session.add(
        Refund(  # noqa: F821
            id=refund_id,
            order_id=order_id,
            amount_cents=requested_cents,
            stripe_refund_id=stripe_refund.id,
            idempotency_key=f"refund-{refund_id}",
        )
    )
    return {"refund_id": refund_id, "amount_cents": requested_cents, "status": "refunded"}
