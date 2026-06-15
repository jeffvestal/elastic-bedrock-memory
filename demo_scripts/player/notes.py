"""
notes.py — right-pane commentary for replay.py.

NOTES maps beat labels (matching REPLAY_BEATS[*]["label"]) to dicts:
  {"headline": str, "bullets": [str, ...]}

Headline: terse, bold — what's happening right now.
Bullets:  plain English, audience-readable from the seats, doubling as Jeff's cues.
"""

NOTES = {
    "act1-placeholder": {
        "headline": "Act 1 — The Amnesiac Agent",
        "bullets": [
            "Stock Kiro has no memory — it reads the code but ignores team decisions.",
            "Gets the code patterns right: cents, idempotency, JWT auth.",
            "But misses every policy rule your team agreed to.",
            "This is the 'before' — every correction is a decision someone already made.",
        ],
    },
    "live-build: create-indices": {
        "headline": "Building the Memory Layer",
        "bullets": [
            "Three Elasticsearch indices: conversation history, knowledge facts, session metadata.",
            "Each uses semantic_text — Jina v5 embeddings, no ELSER, no custom ML setup.",
            "This is the storage. It's just Elasticsearch.",
        ],
    },
    "live-build: create-agent": {
        "headline": "Wiring the Agent + Tools",
        "bullets": [
            "Agent Builder creates the agent and 5 tools via REST API.",
            "4 read tools + 1 write tool (save-knowledge-fact).",
            "The MCP endpoint is live — no custom server code written.",
            "That URL at the bottom is what Kiro will connect to.",
        ],
    },
    "live-build: seed": {
        "headline": "Loading 2 Weeks of History",
        "bullets": [
            "68 docs seeded: 10 sessions, 18 facts, 40 conversation turns.",
            "These are the real decisions: cents vs floats, idempotency keys, JWT auth, Aurora.",
            "This is what gives the agent its memory.",
        ],
    },
    "wire: open mcp.json in vi": {
        "headline": "Wiring Kiro to Elastic",
        "bullets": [
            "One JSON block in ~/.kiro/settings/mcp.json — that's the entire integration.",
            "The URL is the Agent Builder MCP endpoint. Headers handle auth.",
            "No custom MCP server. Agent Builder is the MCP server.",
            "Restart Kiro and the 5 tools are available.",
        ],
    },
    "wire: start kiro": {
        "headline": "Kiro Restarts with Memory",
        "bullets": [
            "kiro-cli picks up the new MCP config on startup.",
            "The 5 Elastic tools are now available — no code written.",
            "Same CLI, same interface — one JSON block changed everything.",
        ],
    },
    "wire: restart Kiro, select agent": {
        "headline": "Selecting the Memory Agent",
        "bullets": [
            "/agent switches Kiro to the checkout-memory configuration.",
            "The same refund prompt is about to run — verbatim.",
            "Watch what Kiro does first, before writing any code.",
        ],
    },
    "Act 2 — refund ask (memory)": {
        "headline": "Same Prompt. Different First Move.",
        "bullets": [
            "Verbatim refund prompt — identical to Act 1.",
            "First move: search-knowledge-facts, not code.",
            "It's asking: what has this team already decided about refunds?",
            "That call is the entire difference between Act 1 and Act 2.",
        ],
    },
    "Act 2 — plan (team decisions)": {
        "headline": "Citing the Team's Decisions",
        "bullets": [
            "Reads the codebase, then surfaces what memory returned.",
            "sess-004-fact-2: partial refunds, cumulative cap, 90-day window.",
            "sess-005-fact-0: integer cents, dollar string at the boundary.",
            "sess-007-fact-0: Stripe idempotency key format.",
        ],
    },
    "Act 2 — write models.py": {
        "headline": "models.py — The Refund Table",
        "bullets": [
            "Adds the Refund SQLAlchemy model to match Aurora schema.",
            "Includes created_at for the 90-day window check.",
            "Idempotency key as a unique column — enforced at DB level.",
        ],
    },
    "Act 2 — write payments.py": {
        "headline": "payments.py — The Stripe Call",
        "bullets": [
            "Adds create_refund() using the same _with_backoff retry helper.",
            "Idempotency key passed through — Stripe deduplicates retries.",
            "Matches the exact pattern of create_charge() already in the file.",
        ],
    },
    "Act 2 — write checkout.py": {
        "headline": "checkout.py — The Endpoint",
        "bullets": [
            "90-day window check. Cumulative cap check. All three policy rules.",
            "dollars_to_cents() at the boundary — integer cents to Stripe and DB.",
            "JWT auth via get_current_user — same as every other route.",
            "None of this was in Act 1. All of it was in memory.",
        ],
    },
    "Act 2 — verify + summary": {
        "headline": "Verification + Audit Trail",
        "bullets": [
            "Re-reads all three changed files to confirm correctness.",
            "Explicitly cites the session IDs behind each decision.",
            "This is what 'memory-aware' looks like — not just code, but provenance.",
        ],
    },
    "Act 2 — write beat (fix idempotency key)": {
        "headline": "A New Decision Just Happened",
        "bullets": [
            "Amount-based idempotency key has a flaw: two $5 refunds on one order collide.",
            "Fix: per-attempt UUID. One-line change.",
            "Now save this decision so the next engineer doesn't rediscover it.",
        ],
    },
    "response: Act 2 — write beat (save UUID rule)": {
        "headline": "Writing to Memory",
        "bullets": [
            "save-knowledge-fact writes the UUID rule back to Elasticsearch.",
            "Fact ID: Wn9ktp4B — this is what Act 3 will retrieve.",
            "The write→read loop is the whole demo. This is the write.",
        ],
    },
    "Act 3 — fresh session, select agent": {
        "headline": "New Session. New Engineer.",
        "bullets": [
            "Kiro has been restarted. Session history is gone.",
            "But the knowledge facts are still in Elasticsearch.",
            "This is the teammate scenario — same question, different context window.",
        ],
    },
    "Act 3 — read-back (teammate)": {
        "headline": "The Question Every Teammate Asks",
        "bullets": [
            "'What's our convention for idempotency keys on refunds?'",
            "Search hits Wn9ktp4B — the fact saved two minutes ago in Act 2.",
            "No Slack thread, no PR comment, no tribal knowledge needed.",
        ],
    },
    "Act 3 — answer": {
        "headline": "Memory Is the Answer",
        "bullets": [
            "refund-{uuid4} — per-attempt UUID, not order+amount.",
            "The agent explains why: two equal partial refunds would collide.",
            "This is the write→read loop closed.",
            "Stateless to stateful. That's the talk.",
        ],
    },
}
