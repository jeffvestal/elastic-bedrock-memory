"""
Demo content for the fake terminal player (see play.py).

This is pure data: an ordered list of Steps that play.py animates. Edit freely.

Provenance per segment:
  - Act 2 + Act 3            -> VERBATIM, transcribed from Jeff's 2026-06-11 Kiro run.
  - Act 1 (amnesiac)         -> RECONSTRUCTED from demo_scripts/reference/refunds-amnesiac.py.
  - Live-build + wire        -> RECONSTRUCTED from the print() output of setup/*.py + seed.py.
Reconstructed steps are marked `# RECONSTRUCTED — swap for real capture`; paste a real
capture over the fragment list to upgrade fidelity.

SEGMENTS exposes each act as its own list so selftest.py can assert per-segment.
STEPS is the concatenation the player runs.
"""
from play import (
    line, blank, rule, tool, toolline, write, code, footer, banner, status,
    idle, sessionend, step_input, step_stream, step_instant,
)

SHELL = "(.venv) ➜  checkout-service-demo git:(main) ✗ "
REPO = "/Users/jeffvestal/repos/checkout-service-demo"

# Verbatim refund prompt (clean canonical text from the run-book; live "refunt" typo dropped).
REFUND_PROMPT = (
    "I need to add refunds to the checkout service. Add a POST endpoint that lets a "
    "customer request a refund on an order — support partial refunds where they can pass "
    "a dollar amount to refund. Wire it up to Stripe."
)


# ---------------------------------------------------------------------------
# Composite helpers — keep the content below readable and DRY.
# ---------------------------------------------------------------------------
def kiro_launch(label):
    """Type `kiro-cli`, then the banner + the first input-box rule."""
    return [
        step_input("kiro-cli", prefix=SHELL, label=f"launch: {label}"),
        step_stream([banner(), blank(), rule()], label=f"banner: {label}"),
    ]


def kiro_turn(prompt, frags, label):
    """One ask: type the prompt, then (enter) stream the response. Ends with a fresh box rule."""
    return [
        step_input(prompt, prefix="  ", label=label),
        step_stream([blank()] + frags + [blank(), rule()], label=f"response: {label}"),
    ]


def kiro_idle_end(agent, resume):
    """The idle input box + status line + 'Session ended'. Its own right-arrow beat:
    response streams -> stops -> [arrow] -> session exits -> stops."""
    return [step_instant(
        [status(agent), blank(), idle(), sessionend(resume)],
        label="session exit", auto=False,
    )]


def shell_cmd(cmd, out_lines, label):
    """A shell command: type it, then stream its stdout line-by-line."""
    return [
        step_input(cmd, prefix=SHELL, label=label),
        step_stream(
            [line(o, indent=0, stream=False) for o in out_lines] + [blank()],
            label=f"output: {label}",
        ),
    ]


# ===========================================================================
# ACT 1 — amnesiac (stock Kiro). Builds the refund endpoint policy-blind.
# RECONSTRUCTED from reference/refunds-amnesiac.py. Gets code patterns right
# (cents, idempotency, JWT, async) but misses the 3 POLICY rules and makes
# NO search-knowledge-facts call. That absence is the whole contrast.
# ===========================================================================
ACT1_RESPONSE = [
    line("I'll add a refund endpoint. Let me read the existing code so I match your patterns."),
    toolline(f"Read {REPO}"),
    toolline("Read (5 files)", detail="models.py, payments.py, checkout.py, money.py, main.py"),
    blank(),
    line("Got it — integer cents, Stripe idempotency + backoff, JWT + ownership, async session. "
         "I'll mirror those. Adding a Refund model, a create_refund in payments.py, and the endpoint:"),
    write(
        f"{REPO}/app/models.py",
        "added 10 lines at L47 in models.py",
        diff=[
            ("+", "47", "class Refund(Base):"),
            ("+", "48", '    __tablename__ = "refunds"'),
            ("+", "49", ""),
            ("+", "50", "    id: Mapped[str] = mapped_column(String, primary_key=True)"),
            ("+", "51", '    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)'),
            ("+", "52", "    amount_cents: Mapped[int] = mapped_column(BigInteger)"),
            ("+", "53", "    stripe_refund_id: Mapped[str | None] = mapped_column(String, nullable=True)"),
            ("+", "54", "    idempotency_key: Mapped[str] = mapped_column(String, unique=True)"),
            ("+", "55", ""),
            (" ", "47", "class WebhookEvent(Base):"),
        ],
    ),
    write(
        f"{REPO}/app/payments.py",
        "added 12 lines, removed 1 line at L68 in payments.py",
        diff=[
            ("-", "68", "# TODO(refunds): no refund path implemented yet."),
            ("+", "68", "def create_refund(*, payment_intent_id: str, amount_cents: int, idempotency_key: str):"),
            ("+", "69", "    return _with_backoff("),
            ("+", "70", "        lambda: stripe.Refund.create("),
            ("+", "71", "            payment_intent=payment_intent_id,"),
            ("+", "72", "            amount=amount_cents,"),
            ("+", "73", "            idempotency_key=idempotency_key,"),
            ("+", "74", "        )"),
            ("+", "75", "    )"),
        ],
    ),
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 37 lines at L60 in checkout.py",
        diff=[
            ("+", "60", "class RefundRequest(BaseModel):"),
            ("+", "61", "    amount: str"),
            ("+", "62", ""),
            ("+", "63", ""),
            ("+", "64", '    @router.post("/orders/{order_id}/refund")'.lstrip()),
            ("+", "65", "async def refund_order("),
            ("+", "66", "    order_id: str,"),
            ("+", "67", "    body: RefundRequest,"),
            ("+", "68", "    user: User = Depends(get_current_user),"),
            ("+", "69", "    session: AsyncSession = Depends(get_session),"),
            ("+", "70", ") -> dict:"),
            ("+", "71", "    order = await session.get(Order, order_id)"),
            ("+", "72", "    if order is None or order.user_id != user.id:"),
            ("+", "73", '        raise HTTPException(status_code=404, detail="Order not found")'),
            ("+", "74", ""),
            ("+", "75", "    amount_cents = dollars_to_cents(body.amount)"),
            ("+", "76", "    if amount_cents <= 0:"),
            ("+", "77", '        raise HTTPException(status_code=400, detail="Refund amount must be positive")'),
            ("+", "78", ""),
            ("+", "79", '    idempotency_key = f"{order_id}-refund-{amount_cents}"'),
            ("+", "80", "    stripe_refund = payments.create_refund("),
            ("+", "81", "        payment_intent_id=order.stripe_payment_intent_id,"),
            ("+", "82", "        amount_cents=amount_cents,"),
            ("+", "83", "        idempotency_key=idempotency_key,"),
            ("+", "84", "    )"),
            ("+", "85", "    session.add(Refund(id=str(uuid.uuid4()), order_id=order_id,"),
            ("+", "86", "                       amount_cents=amount_cents,"),
            ("+", "87", "                       stripe_refund_id=stripe_refund.id,"),
            ("+", "88", "                       idempotency_key=idempotency_key))"),
            ("+", "89", '    return {"order_id": order_id, "refund_id": stripe_refund.id, "amount_cents": amount_cents}'),
        ],
    ),
    blank(),
    line("Done. The refund endpoint mirrors your existing conventions:"),
    blank(),
    line("- Integer cents via dollars_to_cents() at the boundary — no float math.", indent=2),
    line("- JWT auth + ownership check, identical to the checkout route.", indent=2),
    line("- The Stripe call goes through the same _with_backoff helper, with an idempotency key.", indent=2),
    line("- A Refund row is recorded with the Stripe refund id.", indent=2),
    blank(),
    line('The idempotency key is f"{order_id}-refund-{amount_cents}" — stable per order and amount, '
         "so a retried request with the same amount won't double-charge. You're good to go."),
    footer("0.71", "1m 02s"),
]

ACT1 = (
    kiro_launch("Act 1 — stock Kiro")
    + kiro_turn(REFUND_PROMPT, ACT1_RESPONSE, label="Act 1 — refund ask (amnesiac)")
    + kiro_idle_end("Kiro", "a1d2c3b4-0000-4444-8888-ac7a1aaaaaaa")
)


# ===========================================================================
# LIVE-BUILD — build the memory system on camera.
# RECONSTRUCTED from the print() output of the real scripts.
# ===========================================================================
LIVEBUILD = (
    shell_cmd(
        "python3 setup/create-indices.py",
        [
            "Creating indices...",
            "  conversation-history: created",
            "  knowledge-facts: created",
            "  session-metadata: created",
            "Done.",
        ],
        label="live-build: create-indices",
    )
    + shell_cmd(
        "python3 setup/create-agent.py",
        [
            "Creating Agent Builder skill...",
            "  ✓ checkout-memory-retrieval: created",
            "",
            "Creating Agent Builder tools...",
            "  ✓ search-conversation-history: created",
            "  ✓ search-knowledge-facts: created",
            "  ✓ get-recent-conversations: created",
            "  ✓ list-sessions: created",
            "  ✓ save-knowledge-fact: created",
            "",
            "Creating Agent Builder agent...",
            "  ✓ Agent: checkout-service-memory",
            "",
            "✅ Setup complete.",
            "   Agent ID: checkout-service-memory",
            "   Tools: 5 (read + write)",
            "   MCP endpoint:   https://bedrock-memory-demo.kb.us-east-1.aws.elastic.cloud/api/agent_builder/mcp",
        ],
        label="live-build: create-agent",
    )
    + shell_cmd(
        "python3 demo-data/seed.py",
        [
            "Seeding 40 conversation turns, 18 facts, 10 sessions...",
            "Indexed: 68 docs",
            "Done. Run a test query:",
            "  Index: knowledge-facts, conversation-history, session-metadata",
        ],
        label="live-build: seed",
    )
)


# ===========================================================================
# WIRE — add the Agent Builder MCP endpoint to Kiro, select the agent.
# RECONSTRUCTED.
# ===========================================================================
WIRE = shell_cmd(
    "python3 setup/demo-setup.py --add-mcp",
    [
        "=== Adding elastic-memory to mcp.json ===",
        "",
        "  ✓ added 'elastic-memory' → ~/.kiro/settings/mcp.json",
        "  ✓ elastic-memory exposes 5 tools (4 read + save-knowledge-fact)",
        "",
        "  Next: restart Kiro, then /agent → checkout-memory",
    ],
    label="wire: --add-mcp",
)


# ===========================================================================
# ACT 2 — memory-wired Kiro. VERBATIM (2026-06-11 capture).
# ===========================================================================
ACT2_BUILD = [
    tool("search-knowledge-facts", "nlQuery=refund policy partial refunds Stripe"),
    tool("search-knowledge-facts", "nlQuery=money handling currency cents dollars"),
    blank(),
    line("Good — I have the team decisions. Let me read the existing code structure before implementing."),
    toolline(f"Read {REPO}"),
    toolline("Read (5 files)", detail="models.py, payments.py, checkout.py, money.py, main.py"),
    blank(),
    line("I have everything I need. Here's what I'll apply from the team decisions:"),
    blank(),
    line("- sess-004-fact-2: Partial refunds capped at original charge minus prior refunds. "
         "Orders >90 days old → HTTP 422."),
    line("- sess-005-fact-0: Money stored as integer cents; accept dollar string from request, "
         "convert at the boundary."),
    line("- sess-007-fact-0: Stripe calls use exponential backoff + idempotency key. Idempotency key "
         "for refunds = refund-{order_id}-{amount_cents} (stable per request amount)."),
    line("- sess-001-fact-0: Aurora PostgreSQL — need a Refund table."),
    blank(),
    line("I need to: add a Refund model, add create_refund to payments.py, and add the POST endpoint. "
         "Let me implement:"),
    write(
        f"{REPO}/app/models.py",
        "added 11 lines at L47 in models.py",
        diff=[
            ("+", "47", "class Refund(Base):"),
            ("+", "48", '    __tablename__ = "refunds"'),
            ("+", "49", ""),
            ("+", "50", "    id: Mapped[str] = mapped_column(String, primary_key=True)"),
            ("+", "51", '    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)'),
            ("+", "52", "    amount_cents: Mapped[int] = mapped_column(BigInteger)"),
            ("+", "53", "    stripe_refund_id: Mapped[str | None] = mapped_column(String, nullable=True)"),
            ("+", "54", "    idempotency_key: Mapped[str] = mapped_column(String, unique=True)"),
            ("+", "55", "    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),"),
            ("+", "56", ""),
            ("+", "57", ""),
            (" ", "47", "class WebhookEvent(Base):"),
        ],
    ),
    write(
        f"{REPO}/app/payments.py",
        "added 17 lines, removed 1 line at L68 in payments.py",
        diff=[
            ("-", "68", "# TODO(refunds): no refund path implemented yet."),
            ("+", "68", "def create_refund("),
            ("+", "69", "    *,"),
            ("+", "70", "    payment_intent_id: str,"),
            ("+", "71", "    amount_cents: int,"),
            ("+", "72", "    idempotency_key: str,"),
            ("+", "73", ") -> stripe.Refund:"),
            ("+", "74", '    """Issue a (partial) refund against a PaymentIntent.'),
            ("+", "75", ""),
            ("+", "76", "    Idempotency key is stable per order+amount so retries are safe."),
            ("+", "77", '    """'),
            ("+", "78", "    return _with_backoff("),
            ("+", "79", "        lambda: stripe.Refund.create("),
            ("+", "80", "            payment_intent=payment_intent_id,"),
            ("+", "81", "            amount=amount_cents,"),
            ("+", "82", "            idempotency_key=idempotency_key,"),
            ("+", "83", "        )"),
            ("+", "84", "    )"),
        ],
    ),
    line("Now add the refund endpoint to the checkout router:"),
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 74 lines, removed 1 line at L76 in checkout.py",
        diff=[
            ("+", "79", "_REFUND_WINDOW_DAYS = 90"),
            ("+", "82", "class RefundRequest(BaseModel):"),
            ("+", "84", "    amount: str"),
            ("+", "87", '    @router.post("/orders/{order_id}/refunds")'.lstrip()),
            ("+", "88", "async def create_refund("),
            ("+", "89", "    order_id: str,"),
            ("+", "90", "    body: RefundRequest,"),
            ("+", "91", "    user: User = Depends(get_current_user),"),
            ("+", "92", "    session: AsyncSession = Depends(get_session),"),
            ("+", "93", ") -> dict:"),
            ("+", "102", "    order = await session.get(Order, order_id)"),
            ("+", "103", "    if order is None or order.user_id != user.id:"),
            ("+", "104", '        raise HTTPException(status_code=404, detail="Order not found")'),
            ("+", "106", '    if order.status != "paid":'),
            ("+", "107", '        raise HTTPException(status_code=422, detail="Only paid orders can be refunded")'),
            ("+", "109", "    # 90-day window check (sess-004-fact-2)"),
            ("+", "110", "    age_days = (datetime.now(timezone.utc) - order.created_at).days"),
            ("+", "111", "    if age_days > _REFUND_WINDOW_DAYS:"),
            ("+", "114", '            detail="Order is older than 90 days; manager approval required",'),
            ("+", "117", "    refund_cents = dollars_to_cents(body.amount)"),
            ("+", "118", "    if refund_cents <= 0:"),
            ("+", "121", "    # Cap: original charge minus all prior refunds (sess-004-fact-2)"),
            ("+", "122", "    already_refunded = await session.scalar("),
            ("+", "123", "        select(func.coalesce(func.sum(Refund.amount_cents), 0)).where("),
            ("+", "127", "    refundable = order.amount_cents - already_refunded"),
            ("+", "128", "    if refund_cents > refundable:"),
            ("+", "134", '    idempotency_key = f"refund-{order_id}-{refund_cents}"'),
            ("+", "135", "    stripe_refund = payments.create_refund("),
            ("+", "141", "    refund = Refund("),
            ("+", "148", "    session.add(refund)"),
            ("+", "149", '    return {"refund_id": refund.id, "amount_cents": refund_cents, "stripe_refund_id": stripe_refund.id}'),
        ],
    ),
    line("Let me verify the final state of all changed files:"),
    toolline("Read (3 files)", detail="checkout.py, payments.py, models.py"),
    blank(),
    line("Everything looks clean. Here's a summary of what was applied and why:"),
    blank(),
    line("3 files changed:"),
    blank(),
    line("models.py — added Refund table with order_id, amount_cents, stripe_refund_id, "
         "idempotency_key (unique), created_at.", indent=2),
    line("payments.py — added create_refund() using _with_backoff (same retry/jitter pattern "
         "as create_charge).", indent=2),
    line("routers/checkout.py — added POST /orders/{order_id}/refunds.", indent=2),
    blank(),
    line("Team decisions applied:"),
    blank(),
    line("- sess-004-fact-2 (refund policy): partial refunds allowed; capped at "
         "order.amount_cents - sum(prior refunds); orders >90 days → HTTP 422. The endpoint "
         "enforces all three.", indent=2),
    line("- sess-005-fact-0 (integer cents): amount arrives as a dollar string, converted via "
         "dollars_to_cents() at the boundary — Stripe and DB both receive integer cents.", indent=2),
    line("- sess-007-fact-0 (Stripe idempotency): idempotency key is refund-{order_id}-{amount_cents} "
         "— stable per request so retries don't issue duplicate refunds.", indent=2),
    blank(),
    line("One thing to note: you'll need a DB migration to create the refunds table before deploying."),
    footer("0.83", "1m 24s"),
]

STEP7_PROMPT = (
    "One more thing — the refund idempotency key can't be amount-based; two equal partial "
    "refunds would collide. Use a per-attempt UUID (refund-{uuid}). Save that as a decision"
)

ACT2_WRITEBEAT = [
    line("Good catch. Fixing the idempotency key first, then saving the decision."),
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 1 line, removed 1 line at L134 in checkout.py",
        diff=[
            ("-", "134", '    idempotency_key = f"refund-{order_id}-{refund_cents}"'),
            ("+", "134", '    idempotency_key = f"refund-{uuid.uuid4()}"'),
            (" ", "135", "    stripe_refund = payments.create_refund("),
        ],
    ),
    tool(
        "save-knowledge-fact",
        'fact=Refund idempotency key must be a per-attempt UUID (format: "refund-{uuid4}"), '
        "NOT order+amount based — two equal partial refunds on the same order would collide on "
        "an amount-based key and cause the second to be silently deduplicated by Stripe., "
        "category=payments, importance=high, project=checkout-service",
    ),
    code([
        "{",
        '  "content": [',
        "    {",
        "    ...+5 lines (ctrl+o to toggle)",
    ]),
    blank(),
    line('Done. One-line change in checkout.py — idempotency_key = f"refund-{uuid.uuid4()}" — and the '
         "decision is saved to memory. The key is now generated fresh per attempt, so two $5.00 refunds "
         "on the same order each get a unique key and both go through to Stripe correctly."),
    footer("0.23", "23s"),
]

ACT2 = (
    kiro_launch("Act 2 — checkout-memory")
    # RECONSTRUCTED — the /agent pick (the real picker UX differs; refine if desired).
    + kiro_turn(
        "/agent",
        [line("● Switched to agent: checkout-memory", indent=0, style="accent")],
        label="Act 2 — select checkout-memory agent",
    )
    + kiro_turn(REFUND_PROMPT, ACT2_BUILD, label="Act 2 — refund ask (memory)")
    + kiro_turn(STEP7_PROMPT, ACT2_WRITEBEAT, label="Act 2 — write beat (save UUID rule)")
    + kiro_idle_end("checkout-memory", "5f75eac7-974a-466e-8f98-43ba3ab7e324")
)


# ===========================================================================
# ACT 3 — fresh session, cross-session read-back. VERBATIM (clean take).
# ===========================================================================
ACT3_READBACK = [
    tool("search-knowledge-facts", "nlQuery=idempotency keys refunds convention"),
    code([
        "{",
        '  "content": [',
        "    {",
        "    ...+5 lines (ctrl+o to toggle)",
    ]),
    blank(),
    line("The convention is:"),
    blank(),
    line("Format: refund-{uuid4} — a fresh UUID generated per attempt.", indent=2),
    blank(),
    line("Do not use order ID + amount as the key. The reason: two equal partial refunds on the same "
         "order would collide on an amount-based key, causing the second refund to be silently "
         "deduplicated by Stripe."),
    blank(),
    line("Per the stored team decision (fact Wn9ktp4B):", indent=2),
    blank(),
    line('│ "Refund idempotency key must be a per-attempt UUID (refund-{uuid4}), NOT order+amount based."',
         indent=2, style="dim"),
    blank(),
    line("So in practice:"),
    code([
        "import uuid",
        'idempotency_key = f"refund-{uuid.uuid4()}"',
    ]),
    footer("0.07", "14s"),
]

ACT3 = (
    kiro_launch("Act 3 — fresh session")
    # RECONSTRUCTED — re-select the agent in the new session (the lesson from the false start).
    + kiro_turn(
        "/agent",
        [line("● Switched to agent: checkout-memory", indent=0, style="accent")],
        label="Act 3 — select checkout-memory agent",
    )
    + kiro_turn(
        "What's our convention for idempotency keys on refunds?",
        ACT3_READBACK,
        label="Act 3 — read-back (teammate)",
    )
    + kiro_idle_end("checkout-memory", "fa548ab7-a322-4294-af65-eb1d4a30105b")
)


# ---------------------------------------------------------------------------
SEGMENTS = {
    "act1": ACT1,
    "livebuild": LIVEBUILD,
    "wire": WIRE,
    "act2": ACT2,
    "act3": ACT3,
}

STEPS = ACT1 + LIVEBUILD + WIRE + ACT2 + ACT3
