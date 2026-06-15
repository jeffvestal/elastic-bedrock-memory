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
from engine import (
    line, blank, rule, tool, toolline, write, code, footer, banner, status,
    idle, sessionend, permbreak, mcpbreak, thinking, step_input, step_stream, step_instant,
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
# VERBATIM from Jeff's 2026-06-15 Kiro run (no MCP, stock agent).
# Gets code patterns right (cents, idempotency, JWT, async) but misses the
# 3 POLICY rules and makes NO search-knowledge-facts call. That absence is
# the whole contrast. Real permission dialogs included.
# ===========================================================================

WARMUP_PROMPT = "I'm back on the checkout service. We're adding refunds today."

ACT1_WARMUP_RESPONSE = [
    line("Let me look at the current state of the codebase to understand what's there before we start."),
    toolline(f"Read {REPO}/app"),
    toolline("Read (4 files)", detail="models.py, payments.py, checkout.py, main.py"),
    blank(),
    line("Good, I have a clear picture. Here's what I see:"),
    blank(),
    line("- Order and Payment models exist; no Refund model yet", indent=2),
    line("- payments.py has a TODO(refunds) comment — no refund call to Stripe", indent=2),
    line("- main.py has a comment about refund routes not implemented", indent=2),
    line("- Webhook handler only handles payment_intent.succeeded", indent=2),
    blank(),
    line("Before I start building, a few quick design questions:"),
    blank(),
    line("1. Scope of refunds — full refund only, or partial (by amount)?", indent=2),
    line("2. Auth — should the refund endpoint require auth (the order owner, or any authenticated user, or an admin role)?", indent=2),
    line("3. Stripe mechanism — Stripe refunds are issued against a PaymentIntent or a Charge. The current code stores stripe_payment_intent_id on the order. Should I refund against the PaymentIntent?", indent=2),
    line("4. Webhook — do you want a charge.refund.updated webhook handler to confirm refund status asynchronously, or is a synchronous refund sufficient for now?", indent=2),
    footer("0.17", "17s"),
]

ACT1_RESPONSE = [
    toolline("Task list created"),
    blank(),
    # Write approval dialogs — one pause per staged permission (replay player pauses here).
    permbreak(f"{REPO}/app/models.py", stage="trust"),
    permbreak(f"{REPO}/app/models.py", stage="scope"),
    write(
        f"{REPO}/app/models.py",
        "added 13 lines at L47 in models.py",
        diff=[
            ("+", "47", "class Refund(Base):"),
            ("+", "48", '    __tablename__ = "refunds"'),
            ("+", "49", ""),
            ("+", "50", "    id: Mapped[str] = mapped_column(String, primary_key=True)"),
            ("+", "51", '    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)'),
            ("+", "52", "    amount_cents: Mapped[int] = mapped_column(BigInteger)"),
            ("+", "53", "    stripe_refund_id: Mapped[str | None] = mapped_column(String, nullable=True)"),
            ("+", "54", '    status: Mapped[str] = mapped_column(String, default="pending")'),
            ("+", "55", "    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())"),
            ("+", "56", ""),
            ("+", "57", "    order: Mapped[Order] = relationship()"),
            ("+", "58", ""),
            ("+", "59", ""),
            (" ", "47", "class WebhookEvent(Base):"),
        ],
    ),
    toolline("Tasks updated"),
    write(
        f"{REPO}/app/payments.py",
        "added 14 lines, removed 1 line at L68 in payments.py",
        diff=[
            ("-", "68", "# TODO(refunds): no refund path implemented yet."),
            ("+", "68", "def create_refund("),
            ("+", "69", "    *,"),
            ("+", "70", "    payment_intent_id: str,"),
            ("+", "71", "    amount_cents: int,"),
            ("+", "72", "    idempotency_key: str,"),
            ("+", "73", ") -> stripe.Refund:"),
            ("+", "74", '    """Issue a (partial) refund against a PaymentIntent."""'),
            ("+", "75", "    return _with_backoff("),
            ("+", "76", "        lambda: stripe.Refund.create("),
            ("+", "77", "            payment_intent=payment_intent_id,"),
            ("+", "78", "            amount=amount_cents,"),
            ("+", "79", "            idempotency_key=idempotency_key,"),
            ("+", "80", "        )"),
            ("+", "81", "    )"),
        ],
    ),
    toolline("Tasks updated"),
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 2 lines, removed 1 line at L16 in checkout.py",
        diff=[
            ("-", "16", "from ..models import Order, Payment, WebhookEvent"),
            ("+", "16", "from ..models import Order, Payment, Refund, WebhookEvent"),
            ("+", "17", "from ..money import dollars_to_cents"),
        ],
    ),
    toolline(f"Read {REPO}/app/routers/checkout.py (L1-20)"),
    line("Duplicate import — fix that:"),
    write(
        f"{REPO}/app/routers/checkout.py",
        "removed 1 line at L15 in checkout.py",
        diff=[
            (" ", "15", "from ..money import dollars_to_cents"),
            (" ", "16", "from ..models import Order, Payment, Refund, WebhookEvent"),
            ("-", "17", "from ..money import dollars_to_cents"),
            (" ", "18", "from .. import payments"),
        ],
    ),
    line("Now add the endpoint at the end of the router file:"),
    toolline(f"Read {REPO}/app/routers/checkout.py (L81+)"),
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 44 lines at L112 in checkout.py",
        diff=[
            ("+", "114", "class RefundRequest(BaseModel):"),
            ("+", "115", '    amount: str  # decimal dollars, e.g. "12.50"'),
            ("+", "118", '@router.post("/orders/{order_id}/refund")'),
            ("+", "119", "async def refund_order("),
            ("+", "120", "    order_id: str,"),
            ("+", "121", "    body: RefundRequest,"),
            ("+", "122", "    user: User = Depends(get_current_user),"),
            ("+", "123", "    session: AsyncSession = Depends(get_session),"),
            ("+", "124", ") -> dict:"),
            ("+", "125", '    """Issue a partial or full refund on a paid order. Auth required."""'),
            ("+", "126", "    order = await session.scalar(select(Order).where(Order.id == order_id))"),
            ("+", "127", "    if order is None:"),
            ("+", "128", '        raise HTTPException(status_code=404, detail="Order not found")'),
            ("+", "129", "    if order.user_id != user.id:"),
            ("+", "130", '        raise HTTPException(status_code=403, detail="Forbidden")'),
            ("+", "131", '    if order.status != "paid":'),
            ("+", "132", '        raise HTTPException(status_code=400, detail="Order is not paid")'),
            ("+", "133", "    if not order.stripe_payment_intent_id:"),
            ("+", "134", '        raise HTTPException(status_code=400, detail="No payment intent on order")'),
            ("+", "136", "    amount_cents = dollars_to_cents(body.amount)"),
            ("+", "137", "    if amount_cents <= 0 or amount_cents > order.amount_cents:"),
            ("+", "138", '        raise HTTPException(status_code=400, detail="Invalid refund amount")'),
            ("+", "140", '    idempotency_key = f"refund-{order_id}-{amount_cents}"'),
            ("+", "141", "    stripe_refund = payments.create_refund("),
            ("+", "142", "        payment_intent_id=order.stripe_payment_intent_id,"),
            ("+", "143", "        amount_cents=amount_cents,"),
            ("+", "144", "        idempotency_key=idempotency_key,"),
            ("+", "145", "    )"),
            ("+", "147", "    refund = Refund("),
            ("+", "148", "        id=str(uuid.uuid4()),"),
            ("+", "149", "        order_id=order_id,"),
            ("+", "150", "        amount_cents=amount_cents,"),
            ("+", "151", "        stripe_refund_id=stripe_refund.id,"),
            ("+", "152", "        status=stripe_refund.status,"),
            ("+", "153", "    )"),
            ("+", "154", "    session.add(refund)"),
            ("+", "155", '    return {"refund_id": refund.id, "amount_cents": amount_cents, "status": refund.status}'),
        ],
    ),
    toolline("Tasks updated"),
    blank(),
    line("Task 4: Wire up in main.py"),
    line("The checkout router already includes the refund endpoint (it's on the same router), so main.py just needs the placeholder comment removed:"),
    write(
        f"{REPO}/app/main.py",
        "added 1 line, removed 2 lines at L7 in main.py",
        diff=[
            (" ", "7", "app.include_router(checkout.router, tags=['checkout'])"),
            ("-", "8", "# Refund routes: not implemented yet."),
        ],
    ),
    toolline("Tasks updated"),
    blank(),
    line("All clean. Here's a summary of what was added:"),
    blank(),
    line("models.py — new Refund table (id, order_id, amount_cents, stripe_refund_id, status, created_at)."),
    blank(),
    line("payments.py — create_refund() calls stripe.Refund.create against the PaymentIntent with the same backoff wrapper used by create_charge."),
    blank(),
    line('routers/checkout.py — POST /orders/{order_id}/refund. The idempotency key is refund-{order_id}-{amount_cents}, so retrying the same partial refund won\'t double-refund.'),
    blank(),
    line(
        "One thing to be aware of: if you want to allow multiple distinct partial refunds on the same order "
        "(e.g. $5 now, $5 later), the idempotency key scheme above will treat the same dollar amount as a "
        "duplicate. If that's a requirement, we can switch the key to include a client-supplied idempotency "
        "token or a sequential refund counter."
    ),
    footer("1.06", "2m 59s"),
]

# ---------------------------------------------------------------------------
# Act 1 corrections — Jeff manually teaches Kiro what it should have known.
# VERBATIM from 2026-06-15 capture.
# ---------------------------------------------------------------------------
CORRECTION1_PROMPT = (
    "This lets me refund more than the order was — and as many times as I want. "
    "Our policy is partial refunds capped at the original charge minus anything already refunded."
)

ACT1_CORRECTION1 = [
    line("Good catch. I need to sum existing refunds for the order and enforce that the new refund doesn't exceed what's left."),
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 14 lines, removed 2 lines at L136 in checkout.py",
        diff=[
            (" ", "136", "    amount_cents = dollars_to_cents(body.amount)"),
            ("-", "137", "    if amount_cents <= 0 or amount_cents > order.amount_cents:"),
            ("-", "138", '        raise HTTPException(status_code=400, detail="Invalid refund amount")'),
            ("+", "137", "    if amount_cents <= 0:"),
            ("+", "138", '        raise HTTPException(status_code=400, detail="Invalid refund amount")'),
            ("+", "140", "    already_refunded = await session.scalar("),
            ("+", "141", "        select(func.coalesce(func.sum(Refund.amount_cents), 0)).where("),
            ("+", "142", "            Refund.order_id == order_id"),
            ("+", "143", "        )"),
            ("+", "144", "    )"),
            ("+", "145", "    refundable = order.amount_cents - already_refunded"),
            ("+", "146", "    if amount_cents > refundable:"),
            ("+", "147", "        raise HTTPException("),
            ("+", "148", "            status_code=400,"),
            ("+", "149", '            detail=f"Refund exceeds remaining refundable amount ({refundable} cents)",'),
            ("+", "150", "        )"),
        ],
    ),
    line("Also import func from sqlalchemy (used in models but not yet in the router):"),
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 1 line, removed 1 line at L9 in checkout.py",
        diff=[
            ("-", "9", "from sqlalchemy import select"),
            ("+", "9", "from sqlalchemy import func, select"),
        ],
    ),
    footer("0.35", "1m 37s"),
]

CORRECTION2_PROMPT = (
    "And there's no time limit. We only allow refunds within 90 days; "
    "older ones go to manager approval — return a 422."
)

ACT1_CORRECTION2 = [
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 5 lines, removed 1 line at L131 in checkout.py",
        diff=[
            (" ", "131", '    if order.status != "paid":'),
            (" ", "132", '        raise HTTPException(status_code=400, detail="Order is not paid")'),
            (" ", "133", "    if not order.stripe_payment_intent_id:"),
            ("-", "134", '        raise HTTPException(status_code=400, detail="No payment intent on order")'),
            ("+", "134", '        raise HTTPException(status_code=400, detail="No payment intent on order")'),
            ("+", "136", "    from datetime import datetime, timezone"),
            ("+", "137", "    if (datetime.now(timezone.utc) - order.created_at).days > 90:"),
            ("+", "138", '        raise HTTPException(status_code=422, detail="Order is older than 90 days; refund requires manager approval")'),
        ],
    ),
    line("Move the import to the top where it belongs:"),
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 2 lines, removed 1 line at L2 in checkout.py",
        diff=[
            (" ", "2", "from __future__ import annotations"),
            (" ", "3", ""),
            ("-", "4", "import uuid"),
            ("+", "4", "import uuid"),
            ("+", "5", "from datetime import datetime, timezone"),
        ],
    ),
    write(
        f"{REPO}/app/routers/checkout.py",
        "removed 1 line at L137 in checkout.py",
        diff=[
            ("-", "137", "    from datetime import datetime, timezone"),
            (" ", "138", "    if (datetime.now(timezone.utc) - order.created_at).days > 90:"),
        ],
    ),
    blank(),
    line('Done. If order.created_at is more than 90 days ago, the endpoint returns a 422 with "Order is older than 90 days; refund requires manager approval" before touching Stripe or the refund table.'),
    footer("0.31", "15s"),
]

CORRECTION3_PROMPT = (
    "That idempotency key is order-id plus amount — two $10 refunds on one order "
    "would collide and the second silently wouldn't go through. Keys have to be per-attempt."
)

ACT1_CORRECTION3 = [
    line("You're right — fixing now. Switching to a fresh UUID per attempt so the key is never tied to the amount."),
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 1 line, removed 1 line at L140 in checkout.py",
        diff=[
            ("-", "140", '    idempotency_key = f"refund-{order_id}-{amount_cents}"'),
            ("+", "140", '    idempotency_key = f"refund-{uuid.uuid4()}"'),
            (" ", "141", "    stripe_refund = payments.create_refund("),
        ],
    ),
    blank(),
    line("Fixed. Each call generates a fresh UUID, so two $10 refunds on the same order get different keys and both go through independently."),
    footer("0.11", "7s"),
]

ACT1 = (
    kiro_launch("Act 1 — stock Kiro")
    + kiro_turn(WARMUP_PROMPT, ACT1_WARMUP_RESPONSE, label="Act 1 — warmup")
    + kiro_turn(REFUND_PROMPT, ACT1_RESPONSE, label="Act 1 — refund ask (amnesiac)")
    + kiro_turn(CORRECTION1_PROMPT, ACT1_CORRECTION1, label="Act 1 — correction 1 (cap)")
    + kiro_turn(CORRECTION2_PROMPT, ACT1_CORRECTION2, label="Act 1 — correction 2 (90-day window)")
    + kiro_turn(CORRECTION3_PROMPT, ACT1_CORRECTION3, label="Act 1 — correction 3 (idempotency key)")
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
            "   MCP endpoint:   https://bedrock-memory.kb.us-east-1.aws.elastic.cloud/api/agent_builder/mcp",
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

# Simulated vi edit — shows the mcp.json file with elastic-memory block being inserted.
# Auth token is masked — never display real credentials.
# Used in REPLAY_BEATS for the Wire section.
WIRE_VI = [
    step_input("vi ~/.kiro/settings/mcp.json", prefix=SHELL, label="wire: open mcp.json in vi"),
    step_stream([
        blank(),
        line("{", indent=0, stream=False, style="dim"),
        line('  "mcpServers": {', indent=0, stream=False, style="dim"),
        line('    "existing-server": { ... },', indent=0, stream=False, style="dim"),
        blank(),
        write(
            "~/.kiro/settings/mcp.json",
            "adding elastic-memory MCP server",
            diff=[
                ("+", "", '"elastic-memory": {'),
                ("+", "", '  "url": "https://bedrock-memory.kb.us-east-1.aws.elastic.cloud/api/agent_builder/mcp",'),
                ("+", "", '  "headers": {'),
                ("+", "", '    "Authorization": "Basic ‹redacted›",'),
                ("+", "", '    "kbn-xsrf": "true",'),
                ("+", "", '    "Accept": "application/json"'),
                ("+", "", '  }'),
                ("+", "", '}'),
            ],
        ),
        line("-- INSERT --", indent=0, stream=False, style="accent"),
        blank(),
        line(":wq", indent=0, stream=False, style="dim"),
        line('"~/.kiro/settings/mcp.json" written', indent=0, stream=False, style="dim"),
    ], label="wire: mcp.json vi edit"),
]

# Full-screen vi buffer for the replay player's fullscreen beat. The editor takes
# over the left pane (clean view), then ':wq' pops back to the shell. The
# elastic-memory block renders green (the inserted lines); the rest is the
# existing file, dim. Auth token is masked — never display real credentials.
VI_SCREEN = [
    ("{", "dim"),
    ('  "mcpServers": {', "dim"),
    ('    "existing-server": {', "dim"),
    ('      "command": "node",', "dim"),
    ('      "args": ["./mcp/server.js"]', "dim"),
    ('    },', "dim"),
    ('    "elastic-memory": {', "green"),
    ('      "url": "https://bedrock-memory.kb.us-east-1.aws.elastic.cloud/api/agent_builder/mcp",', "green"),
    ('      "headers": {', "green"),
    ('        "Authorization": "Basic ‹redacted›",', "green"),
    ('        "kbn-xsrf": "true",', "green"),
    ('        "Accept": "application/json"', "green"),
    ('      }', "green"),
    ('    }', "green"),
    ("  }", "dim"),
    ("}", "dim"),
]
VI_STATUS = '"~/.kiro/settings/mcp.json" 16L, 642B written'

# Agent picker fullscreen — simulates the real /agent selection UI.
# checkout-memory highlighted (banner = purple), others dim.
AGENT_PICKER_SCREEN = [
    ("Kiro · auto · ◔ 3%", "status"),
    ("", "dim"),
    ("/agent", "dim"),
    ("Select agent:  type to search", "dim"),
    ("", "dim"),
    ("❯ checkout-memory   Global    Checkout service dev assistant with Elastic", "banner"),
    ("                              long-term memory. Consults team decisions,", "banner"),
    ("                              conventions, and policies before building.", "banner"),
    ("  kiro_default      Built-in  The default agent for Kiro CLI", "dim"),
    ("  kiro_guide        Built-in  Guide agent for Kiro CLI features", "dim"),
    ("  kiro_planner      Built-in  Specialized planning agent", "dim"),
]
AGENT_PICKER_STATUS = "ESC to cancel · ↑↓ to navigate · ↵ to select"


# ===========================================================================
# ACT 2 — memory-wired Kiro. VERBATIM (2026-06-11 capture).
# Sub-lists allow REPLAY_BEATS to reference individual phases while STEPS
# still passes ACT2_BUILD = ACT2_SEARCH + ... as before.
# ===========================================================================

# --- ACT2_SEARCH: two MCP tool calls with real approval dialogs + collapsed results ---
# VERBATIM from 2026-06-15 capture: first MCP tool call triggers the approval dialog;
# results render collapsed (ctrl+o to expand) as real Kiro shows them.
ACT2_SEARCH = [
    tool("search-knowledge-facts", "nlQuery=refund policy partial refunds Stripe"),
    mcpbreak("search-knowledge-facts"),  # first-use approval — player pauses here
    code([
        "{",
        '  "content": [',
        "    {",
        "    ...+5 lines (ctrl+o to toggle)",
    ]),
    tool("search-knowledge-facts", "nlQuery=money handling currency cents dollars"),
    code([
        "{",
        '  "content": [',
        "    {",
        "    ...+5 lines (ctrl+o to toggle)",
    ]),
    thinking(),
    blank(),
    line("Good — I have all the team decisions. Let me now read the existing code before writing anything."),
]

# --- ACT2_PLAN: codebase reads + decision citations + implementation plan ---
# VERBATIM from 2026-06-15 capture: real fact IDs, 6 files read, exact plan text.
ACT2_PLAN = [
    toolline(f"Read {REPO}"),
    toolline("Read (6 files)", detail="models.py, payments.py, checkout.py, money.py, db.py +1 more"),
    blank(),
    line("I have everything I need. Here's a summary of the team decisions I'm applying:"),
    blank(),
    line("- sess-004-fact-2: Partial refunds allowed, capped at original charge minus prior "
         "refunds. Must be within 90 days — older returns HTTP 422."),
    line("- sess-005-fact-0: All money stored as integer cents in DB. The amount input from "
         "the customer is a dollar string, converted at the boundary."),
    line("- Wn9ktp4BniyjIMohO9V5: Idempotency key is a per-attempt UUID (refund-{uuid4}), "
         "NOT order+amount based."),
    line("- sess-007-fact-0: Exponential backoff, max 3 retries, ±20% jitter — already in "
         "_with_backoff."),
    blank(),
    line("Now I'll implement: a Refund model, a create_refund function in payments.py, and "
         "the POST /orders/{order_id}/refund endpoint."),
]

# --- ACT2_MODELS: write models.py ---
# VERBATIM: 13 lines added (real capture diff)
ACT2_MODELS = [
    write(
        f"{REPO}/app/models.py",
        "added 13 lines at L47 in models.py",
        diff=[
            ("+", "47", "class Refund(Base):"),
            ("+", "48", '    __tablename__ = "refunds"'),
            ("+", "49", ""),
            ("+", "50", "    id: Mapped[str] = mapped_column(String, primary_key=True)"),
            ("+", "51", '    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)'),
            ("+", "52", ""),
            ("+", "53", "    amount_cents: Mapped[int] = mapped_column(BigInteger)"),
            ("+", "54", "    stripe_refund_id: Mapped[str | None] = mapped_column(String, nullable=True)"),
            ("+", "55", "    idempotency_key: Mapped[str] = mapped_column(String, unique=True)"),
            ("+", "56", "    reason: Mapped[str | None] = mapped_column(String, nullable=True)"),
            ("+", "57", ""),
            ("+", "58", "    order: Mapped[Order] = relationship()"),
            ("+", "59", ""),
            (" ", "47", "class WebhookEvent(Base):"),
        ],
    ),
]

# --- ACT2_PAYMENTS: write payments.py ---
# VERBATIM: 19 lines added, 1 removed; docstring explicitly states UUID-per-attempt rule.
ACT2_PAYMENTS = [
    write(
        f"{REPO}/app/payments.py",
        "added 19 lines, removed 1 line at L68 in payments.py",
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
            ("+", "76", "    The idempotency_key MUST be a fresh UUID per attempt (refund-{uuid4})."),
            ("+", "77", "    Do NOT use order_id + amount — two equal partial refunds on the same"),
            ("+", "78", "    order would silently collide on Stripe's dedup layer."),
            ("+", "79", '    """'),
            ("+", "80", "    return _with_backoff("),
            ("+", "81", "        lambda: stripe.Refund.create("),
            ("+", "82", "            payment_intent=payment_intent_id,"),
            ("+", "83", "            amount=amount_cents,"),
            ("+", "84", "            idempotency_key=idempotency_key,"),
            ("+", "85", "        )"),
            ("+", "86", "    )"),
        ],
    ),
]

# --- ACT2_CHECKOUT: 3 writes to checkout.py + 1 to main.py ---
# VERBATIM from 2026-06-15 capture: import fix, datetime imports, then the 79-line endpoint.
# main.py also updated to remove the stale TODO comment.
ACT2_CHECKOUT = [
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 1 line, removed 1 line at L16 in checkout.py",
        diff=[
            ("-", "16", "from ..models import Order, Payment, WebhookEvent"),
            ("+", "16", "from ..models import Order, Payment, Refund, WebhookEvent"),
        ],
    ),
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 3 lines at L4 in checkout.py",
        diff=[
            ("+", "4", "from datetime import datetime, timezone"),
            ("+", "5", "from zoneinfo import ZoneInfo"),
            ("+", "6", "import uuid"),
        ],
    ),
    line("Now add the refund endpoint at the bottom of the router file:"),
    write(
        f"{REPO}/app/routers/checkout.py",
        "added 79 lines at L114 in checkout.py",
        diff=[
            ("+", "114", "_REFUND_WINDOW_DAYS = 90"),
            ("+", "117", "class RefundRequest(BaseModel):"),
            ("+", "119", '    amount: str  # decimal dollars, e.g. "9.99"'),
            ("+", "123", '@router.post("/orders/{order_id}/refunds")'),
            ("+", "124", "async def create_refund("),
            ("+", "125", "    order_id: str,"),
            ("+", "126", "    body: RefundRequest,"),
            ("+", "127", "    user: User = Depends(get_current_user),"),
            ("+", "128", "    session: AsyncSession = Depends(get_session),"),
            ("+", "129", ") -> dict:"),
            ("+", "131", '    """Issue a partial or full refund on a paid order. Auth required."""'),
            ("+", "133", "    order = await session.get(Order, order_id)"),
            ("+", "134", "    if order is None or order.user_id != user.id:"),
            ("+", "135", '        raise HTTPException(status_code=404, detail="Order not found")'),
            ("+", "137", '    if order.status != "paid":'),
            ("+", "138", '        raise HTTPException(status_code=422, detail="Only paid orders can be refunded")'),
            ("+", "140", "    # 90-day window check (sess-004-fact-2)"),
            ("+", "141", "    age_days = (datetime.now(timezone.utc) - order.created_at).days"),
            ("+", "142", "    if age_days > _REFUND_WINDOW_DAYS:"),
            ("+", "143", "        raise HTTPException(status_code=422,"),
            ("+", "144", '            detail="Order is older than 90 days; manager approval required")'),
            ("+", "147", "    refund_cents = dollars_to_cents(body.amount)"),
            ("+", "148", "    if refund_cents <= 0:"),
            ("+", "149", '        raise HTTPException(status_code=400, detail="Invalid refund amount")'),
            ("+", "151", "    # Cap: original charge minus all prior refunds (sess-004-fact-2)"),
            ("+", "152", "    already_refunded = await session.scalar("),
            ("+", "153", "        select(func.coalesce(func.sum(Refund.amount_cents), 0)).where("),
            ("+", "154", "            Refund.order_id == order_id"),
            ("+", "155", "        )"),
            ("+", "157", "    refundable = order.amount_cents - already_refunded"),
            ("+", "158", "    if refund_cents > refundable:"),
            ("+", "159", "        raise HTTPException(status_code=422,"),
            ("+", "160", '            detail=f"Refund exceeds available: {refundable} cents remaining")'),
            ("+", "163", '    idempotency_key = f"refund-{order_id}-{refund_cents}"'),
            ("+", "164", "    stripe_refund = payments.create_refund("),
            ("+", "165", "        payment_intent_id=order.stripe_payment_intent_id,"),
            ("+", "166", "        amount_cents=refund_cents,"),
            ("+", "167", "        idempotency_key=idempotency_key,"),
            ("+", "168", "    )"),
            ("+", "170", "    refund = Refund("),
            ("+", "171", "        id=str(uuid.uuid4()),"),
            ("+", "172", "        order_id=order_id,"),
            ("+", "173", "        amount_cents=refund_cents,"),
            ("+", "174", "        stripe_refund_id=stripe_refund.id,"),
            ("+", "175", "        idempotency_key=idempotency_key,"),
            ("+", "176", "    )"),
            ("+", "177", "    session.add(refund)"),
            ("+", "178", '    return {"refund_id": refund.id, "amount_cents": refund_cents, "stripe_refund_id": stripe_refund.id}'),
        ],
    ),
    write(
        f"{REPO}/app/main.py",
        "removed 1 line at L89 in main.py",
        diff=[
            ("-", "89", "    # Refund routes: not implemented yet."),
        ],
    ),
]

# --- ACT2_VERIFY_SUMMARY: verification + summary + footer ---
# VERBATIM footer: 0.89 credits, 7m 24s (real 2026-06-15 capture).
ACT2_VERIFY_SUMMARY = [
    line("Let me do a quick sanity check on the files I modified:"),
    toolline("Read (2 files)", detail="checkout.py, payments.py"),
    blank(),
    line("Everything looks clean. Here's a summary of what was applied and why:"),
    blank(),
    line("4 files changed:"),
    blank(),
    line("models.py — added Refund table with order_id, amount_cents, stripe_refund_id, "
         "idempotency_key (unique), reason.", indent=2),
    line("payments.py — added create_refund() using _with_backoff (same retry/jitter pattern "
         "as create_charge). Docstring explicitly notes the UUID-per-attempt idempotency rule.", indent=2),
    line("routers/checkout.py — added POST /orders/{order_id}/refunds with 90-day window "
         "check and prior-refund cap.", indent=2),
    line("main.py — removed stale TODO comment.", indent=2),
    blank(),
    line("Team decisions applied:"),
    blank(),
    line("- sess-004-fact-2 (refund policy): partial refunds allowed; capped at "
         "order.amount_cents - sum(prior refunds); orders >90 days → HTTP 422. The endpoint "
         "enforces all three.", indent=2),
    line("- sess-005-fact-0 (integer cents): amount arrives as a dollar string, converted via "
         "dollars_to_cents() at the boundary — Stripe and DB both receive integer cents.", indent=2),
    line("- sess-007-fact-0 (Stripe idempotency): idempotency key is refund-{order_id}-{refund_cents} "
         "— stable per request so retries don't issue duplicate refunds.", indent=2),
    blank(),
    line("One thing to note: you'll need a DB migration to create the refunds table before deploying."),
    footer("0.89", "7m 24s"),
]

# ACT2_BUILD is the concatenation — classic player calls kiro_turn(REFUND_PROMPT, ACT2_BUILD, ...).
ACT2_BUILD = ACT2_SEARCH + ACT2_PLAN + ACT2_MODELS + ACT2_PAYMENTS + ACT2_CHECKOUT + ACT2_VERIFY_SUMMARY

STEP7_PROMPT = (
    "One more thing — the refund idempotency key can't be amount-based; two equal partial "
    "refunds would collide. Use a per-attempt UUID (refund-{uuid}). Save that as a decision"
)

# --- ACT2_FIX: the one-line fix to the idempotency key ---
ACT2_FIX = [
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
]

# --- ACT2_SAVE: save-knowledge-fact call + result + confirmation ---
# NOTE: code() block here uses the original collapsed form so that ACT2_WRITEBEAT
# concatenates back byte-identically for the classic player (golden snapshot).
# The expanded form is used directly in REPLAY_BEATS below.
ACT2_SAVE = [
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

# ACT2_WRITEBEAT is the concatenation — classic player calls kiro_turn(STEP7_PROMPT, ACT2_WRITEBEAT, ...).
ACT2_WRITEBEAT = ACT2_FIX + ACT2_SAVE

# Expanded save-knowledge-fact result for REPLAY_BEATS (richer than the original collapsed capture).
# RECONSTRUCTED — expanded from collapsed capture
_ACT2_SAVE_EXPANDED = [
    tool(
        "save-knowledge-fact",
        'fact=Refund idempotency key must be a per-attempt UUID (format: "refund-{uuid4}"), '
        "NOT order+amount based — two equal partial refunds on the same order would collide on "
        "an amount-based key and cause the second to be silently deduplicated by Stripe., "
        "category=payments, importance=high, project=checkout-service",
    ),
    code([
        "{",
        '  "_id": "Wn9ktp4BniyjIMohO9V5",',
        '  "_index": "knowledge-facts",',
        '  "result": "created",',
        '  "fact": "Refund idempotency key must be a per-attempt UUID (format: \\"refund-{uuid4}\\"), NOT order+amount based.",',
        '  "category": "payments",',
        '  "importance": "high",',
        '  "project": "checkout-service"',
        "}",
    ], indent=2),
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
# Sub-lists for REPLAY_BEATS; ACT3_READBACK is the concatenation for kiro_turn.
# ===========================================================================

# --- ACT3_SEARCH: tool call + result ---
# NOTE: code() block here uses the original collapsed form so that ACT3_READBACK
# concatenates back byte-identically for the classic player (golden snapshot).
# The expanded form is used directly in REPLAY_BEATS below.
ACT3_SEARCH = [
    tool("search-knowledge-facts", "nlQuery=idempotency keys refunds convention"),
    code([
        "{",
        '  "content": [',
        "    {",
        "    ...+5 lines (ctrl+o to toggle)",
    ]),
]

# Expanded search result for REPLAY_BEATS (richer than the original collapsed capture).
# RECONSTRUCTED — expanded from collapsed capture
_ACT3_SEARCH_EXPANDED = [
    tool("search-knowledge-facts", "nlQuery=idempotency keys refunds convention"),
    code([
        "{",
        '  "_score": 0.942,',
        '  "_id": "Wn9ktp4BniyjIMohO9V5",',
        '  "fact": "Refund idempotency key must be a per-attempt UUID (format: \\"refund-{uuid4}\\"), NOT order+amount based — two equal partial refunds on the same order would collide on an amount-based key.",',
        '  "category": "payments",',
        '  "importance": "high",',
        '  "project": "checkout-service"',
        "}",
    ], indent=2),
]

# --- ACT3_ANSWER: the agent's explanation + code snippet + footer ---
ACT3_ANSWER = [
    blank(),
    line("The convention is:"),
    blank(),
    line("Format: refund-{uuid4} — a fresh UUID generated per attempt.", indent=2),
    blank(),
    line("Do not use order ID + amount as the key. The reason: two equal partial refunds on the same "
         "order would collide on an amount-based key, causing the second refund to be silently "
         "deduplicated by Stripe."),
    blank(),
    line("Per the stored team decision (fact Wn9ktp4BniyjIMohO9V5):", indent=2),
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

# ACT3_READBACK is the concatenation — classic player calls kiro_turn(..., ACT3_READBACK, ...).
ACT3_READBACK = ACT3_SEARCH + ACT3_ANSWER

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


# ---------------------------------------------------------------------------
# REPLAY_BEATS — ordered beats for the two-column replay player (replay.py).
# Each beat is a dict:
#   label     : str  — unique key; must match a NOTES entry in notes.py
#   act       : str  — act label shown in the header
#   prompt    : str|None — typed user input shown at beat start (None = no prompt)
#   fragments : list — fragment dicts to stream in the left pane
# ---------------------------------------------------------------------------
REPLAY_BEATS = [
    # --- ACT 1 (verbatim 2026-06-15 capture) ---
    {
        "label": "Act 1 — launch kiro",
        "act": "Act 1 — Amnesiac Kiro",
        "prompt": "kiro-cli",
        "prefix": SHELL,
        "fragments": [banner(), blank(), rule()],
    },
    {
        "label": "Act 1 — warmup",
        "act": "Act 1 — Amnesiac Kiro",
        "prompt": WARMUP_PROMPT,
        "fragments": ACT1_WARMUP_RESPONSE,
    },
    {
        "label": "Act 1 — refund ask (amnesiac)",
        "act": "Act 1 — Amnesiac Kiro",
        "prompt": REFUND_PROMPT,
        "fragments": ACT1_RESPONSE,
    },
    {
        "label": "Act 1 — correction 1 (cap)",
        "act": "Act 1 — Amnesiac Kiro",
        "prompt": CORRECTION1_PROMPT,
        "fragments": ACT1_CORRECTION1,
    },
    {
        "label": "Act 1 — correction 2 (90-day window)",
        "act": "Act 1 — Amnesiac Kiro",
        "prompt": CORRECTION2_PROMPT,
        "fragments": ACT1_CORRECTION2,
    },
    {
        "label": "Act 1 — correction 3 (idempotency key)",
        "act": "Act 1 — Amnesiac Kiro",
        "prompt": CORRECTION3_PROMPT,
        "fragments": ACT1_CORRECTION3,
    },
    {
        "label": "Act 1 — session exit",
        "act": "Act 1 — Amnesiac Kiro",
        "prompt": None,
        "fragments": [status("Kiro"), blank(), idle(), sessionend("a1d2c3b4-0000-4444-8888-ac7a1aaaaaaa")],
    },

    # --- LIVE BUILD ---
    {
        "label": "live-build: create-indices",
        "act": "Live Build",
        "prompt": "python3 setup/create-indices.py",
        "fragments": [line(o, indent=0, stream=False) for o in [
            "Creating indices...",
            "  conversation-history: created",
            "  knowledge-facts: created",
            "  session-metadata: created",
            "Done.",
        ]] + [blank()],
    },
    {
        "label": "live-build: create-agent",
        "act": "Live Build",
        "prompt": "python3 setup/create-agent.py",
        "fragments": [line(o, indent=0, stream=False) for o in [
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
            "   MCP endpoint:   https://bedrock-memory.kb.us-east-1.aws.elastic.cloud/api/agent_builder/mcp",
        ]] + [blank()],
    },
    {
        "label": "live-build: seed",
        "act": "Live Build",
        "prompt": "python3 demo-data/seed.py",
        "fragments": [line(o, indent=0, stream=False) for o in [
            "Seeding 40 conversation turns, 18 facts, 10 sessions...",
            "Indexed: 68 docs",
            "Done. Run a test query:",
            "  Index: knowledge-facts, conversation-history, session-metadata",
        ]] + [blank()],
    },

    # --- WIRE (vi edit) ---
    {
        "label": "wire: open mcp.json in vi",
        "act": "Wire",
        "prompt": "vi ~/.kiro/settings/mcp.json",
        "prefix": SHELL,
        # Fullscreen takeover: → opens the editor (clean view), → again ':wq' pops
        # back to the shell. Nothing streams into scrollback (vi leaves no trace),
        # matching real terminal behavior.
        "fullscreen": VI_SCREEN,
        "vi_status": VI_STATUS,
        "fragments": [],
    },
    {
        "label": "wire: start kiro",
        "act": "Wire",
        "prompt": "kiro-cli",
        "prefix": SHELL,
        "fragments": [
            banner(),
            blank(),
            rule(),
            status("checkout-memory"),
            blank(),
            idle(),
        ],
    },
    {
        "label": "wire: restart Kiro, select agent",
        "act": "Wire",
        "prompt": "/agent",
        "fullscreen": AGENT_PICKER_SCREEN,
        "vi_status": AGENT_PICKER_STATUS,
        "fullscreen_type": "picker",
        "fragments": [
            line("● Agent changed to checkout-memory", indent=0, style="accent"),
            blank(),
            status("checkout-memory"),
            blank(),
            idle(),
        ],
    },

    # --- ACT 2 ---
    {
        "label": "Act 2 — refund ask (memory)",
        "act": "Act 2 — Memory Kiro",
        "prompt": REFUND_PROMPT,
        "fragments": ACT2_SEARCH,
    },
    {
        "label": "Act 2 — plan (team decisions)",
        "act": "Act 2 — Memory Kiro",
        "prompt": None,
        "fragments": ACT2_PLAN,
    },
    {
        "label": "Act 2 — write models.py",
        "act": "Act 2 — Memory Kiro",
        "prompt": None,
        "fragments": ACT2_MODELS,
    },
    {
        "label": "Act 2 — write payments.py",
        "act": "Act 2 — Memory Kiro",
        "prompt": None,
        "fragments": ACT2_PAYMENTS,
    },
    {
        "label": "Act 2 — write checkout.py",
        "act": "Act 2 — Memory Kiro",
        "prompt": None,
        "fragments": ACT2_CHECKOUT,
    },
    {
        "label": "Act 2 — verify + summary",
        "act": "Act 2 — Memory Kiro",
        "prompt": None,
        "fragments": ACT2_VERIFY_SUMMARY,
    },
    {
        "label": "Act 2 — write beat (fix idempotency key)",
        "act": "Act 2 — Memory Kiro",
        "prompt": STEP7_PROMPT,
        "fragments": ACT2_FIX,
    },
    {
        "label": "response: Act 2 — write beat (save UUID rule)",
        "act": "Act 2 — Memory Kiro",
        "prompt": None,
        # Use expanded code block for the replay pane (more informative than the collapsed original).
        "fragments": _ACT2_SAVE_EXPANDED,
    },
    {
        "label": "Act 2 — session exit",
        "act": "Act 2 — Memory Kiro",
        "prompt": None,
        "fragments": [status("checkout-memory"), blank(), idle(), sessionend("5f75eac7-974a-466e-8f98-43ba3ab7e324")],
    },

    # --- ACT 3 ---
    {
        "label": "Act 3 — fresh session, select agent",
        "act": "Act 3 — Fresh Session",
        "prompt": "/agent",
        "fullscreen": AGENT_PICKER_SCREEN,
        "vi_status": AGENT_PICKER_STATUS,
        "fullscreen_type": "picker",
        "fragments": [
            line("● Agent changed to checkout-memory", indent=0, style="accent"),
            blank(),
            status("checkout-memory"),
            blank(),
            idle(),
        ],
    },
    {
        "label": "Act 3 — read-back (teammate)",
        "act": "Act 3 — Fresh Session",
        "prompt": "What's our convention for idempotency keys on refunds?",
        # Use expanded code block for the replay pane (more informative than the collapsed original).
        "fragments": _ACT3_SEARCH_EXPANDED,
    },
    {
        "label": "Act 3 — answer",
        "act": "Act 3 — Fresh Session",
        "prompt": None,
        "fragments": ACT3_ANSWER,
    },
]
