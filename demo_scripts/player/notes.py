"""
notes.py — right-pane commentary for replay.py.

NOTES maps beat labels (matching REPLAY_BEATS[*]["label"]) to dicts:
  {"headline": str, "bullets": [str, ...], "commentary": str}

Headline:   terse, bold — what's happening right now.
Bullets:    plain English, audience-readable from the seats, doubling as Jeff's cues.
Commentary: 2-3 sentences. The "why should I care" paragraph — written so a
            developer who just photographed the screen understands the stakes.
"""

NOTES = {
    "Act 1 — launch kiro": {
        "headline": "Stock Kiro — No Persistent Memory",
        "bullets": [
            "Stock Kiro: no MCP wired, no elastic-memory in mcp.json.",
            "Default agent — no checkout-memory skill loaded.",
            "In-session context works fine. Cross-session decisions: gone.",
            "This is the baseline every developer starts with.",
        ],
        "commentary": (
            "This is the agent every team is shipping with today: a capable model "
            "with no persistent record of decisions your team has made in past sessions. "
            "It will happily rebuild things you already solved, because each new session "
            "starts with only what's in the codebase right now. Hold this baseline in "
            "your head — in ten minutes the exact same agent, same prompt, behaves "
            "completely differently."
        ),
    },
    "Act 1 — warmup": {
        "headline": "Kiro Reads the Repo",
        "bullets": [
            "Stock Kiro — no MCP wired, no persistent memory tools.",
            "Reads the codebase correctly: payments.py, models.py, checkout.py.",
            "Identifies what's missing, then asks three clarifying questions.",
            "Pattern recognition works. Institutional memory is what's gone.",
        ],
        "commentary": (
            "Notice the agent is genuinely good at reading code — it parses the service, "
            "spots the missing refund path, asks sharp questions. The gap was never raw "
            "intelligence. The gap is that it can read the files in front of it but has no "
            "access to the reasoning that produced them — the bug post-mortems, the "
            "Slack arguments, the decisions that never made it into a comment."
        ),
    },
    "Act 1 — refund ask (amnesiac)": {
        "headline": "The Amnesiac Agent Builds It",
        "bullets": [
            "Zero memory tool calls — those tools don't exist yet.",
            "Gets code patterns right: integer cents, JWT auth, Stripe backoff.",
            "Idempotency key: refund-{order_id}-{amount_cents}. Amount-based. The bug.",
            "No 90-day window. No cumulative refund cap. Policy-blind.",
            "Even Kiro notes the key scheme has a limitation — but still ships it.",
        ],
        "commentary": (
            "This is the dangerous failure mode — not code that's obviously broken, but "
            "code that looks production-ready and is quietly wrong on policy. The "
            "amount-based idempotency key means two legitimate $5 partial refunds on the "
            "same order collide and one silently fails; there's no 90-day window and no cap, "
            "so the endpoint will refund a customer more than they ever paid. The agent isn't "
            "dumb — it just never knew these rules existed, so a human has to catch every one."
        ),
    },
    "Act 1 — correction 1 (cap)": {
        "headline": "Correction 1 — No Refund Cap",
        "bullets": [
            "Jeff: 'This lets me refund more than the order was.'",
            "Stock Kiro had no idea the team set a cumulative cap.",
            "Kiro adds the cap + func import. The idempotency key is still wrong.",
            "That's one bug down. Two more to go.",
        ],
        "commentary": (
            "The refund cap is the highest-stakes miss: without it, a customer could receive "
            "multiple refunds totalling more than their original payment. This isn't a subtle "
            "edge case — it's a fundamental policy the team recorded in sess-004-fact-2. Stock "
            "Kiro can't see that session, so Jeff has to catch it in review. The fix lands, but "
            "notice what didn't change: the idempotency key is still order-id plus amount. "
            "That bug needs its own correction."
        ),
    },
    "Act 1 — correction 2 (90-day window)": {
        "headline": "Correction 2 — No Time Window",
        "bullets": [
            "Jeff: 'We only allow refunds within 90 days.'",
            "Another policy from sess-004-fact-2 — same session, second miss.",
            "Without this, old orders refund forever. Accounting nightmare.",
            "A memory-wired agent would have read this before touching a file.",
        ],
        "commentary": (
            "The 90-day window and the refund cap live in the same seeded fact — sess-004-fact-2 "
            "— yet this is a separate correction because the agent had no way to apply a rule it "
            "never read. That's the compounding cost: one missing memory source means all the "
            "decisions that came out of that session get re-taught by hand, one by one, in code "
            "review. The lesson isn't 'Kiro made a mistake'; it's 'the decision never made it "
            "into a place the agent could reach.'"
        ),
    },
    "Act 1 — correction 3 (idempotency key)": {
        "headline": "Correction 3 — The Idempotency Bug",
        "bullets": [
            "Jeff: 'Two $10 refunds on one order would collide. Keys have to be per-attempt.'",
            "Stock Kiro even flagged this limitation in its own summary — and still shipped it.",
            "Kiro fixes it now: refund-{uuid4()} — a fresh UUID per attempt.",
            "3 corrections, 3 policies. None were in the codebase. All were in memory.",
        ],
        "commentary": (
            "This is the closing argument for Act 1: three corrections, three policies, zero of "
            "them in the codebase. Every one lived in past sessions — in facts the agent could "
            "have retrieved if memory existed. The idempotency bug is particularly pointed because "
            "Kiro explicitly flagged the limitation in its own summary and still shipped the bad "
            "scheme. Confidence without context is what memory is designed to fix. In Act 2, the "
            "same prompt, same agent — but it reads memory first."
        ),
    },
    "Act 1 — session exit": {
        "headline": "Act 1 Ends — Nothing Persisted",
        "bullets": [
            "Stock Kiro exits. No persistent store — nothing survives this session.",
            "Every correction the developer made lives only in chat scrollback.",
            "Next session, next teammate: same blind spots, same corrections.",
            "This is the tax you pay on every stateless agent, every day.",
        ],
        "commentary": (
            "Everything the developer just taught this agent — the cap, the window, the key "
            "collision — evaporates the moment the session closes. Tomorrow it makes the same "
            "mistakes; so does the next teammate who picks up a similar ticket. That's the real "
            "cost of stateless tooling: it isn't one bad answer, it's the same lesson re-taught "
            "forever, by every person, in every session."
        ),
    },
    "live-build: create-indices": {
        "headline": "Building the Memory Layer",
        "bullets": [
            "Three Elasticsearch indices: conversation-history, knowledge-facts, session-metadata.",
            "Each uses semantic_text — Jina v5 embeddings, no ELSER, no ML pipeline to babysit.",
            "Semantic search out of the box: ask in plain English, match on meaning.",
            "This is the storage tier. It's just Elasticsearch.",
        ],
        "commentary": (
            "The memory layer isn't an exotic new database — it's three Elasticsearch indices "
            "with a semantic_text field, which means embeddings and vector search are handled "
            "for you without standing up a model-serving stack. Facts go in as plain text and "
            "come back by meaning, so 'how do we handle refund retries' finds the right decision "
            "even if nobody used that exact phrasing. Storage was never the hard part; recall is."
        ),
    },
    "live-build: create-agent": {
        "headline": "Wiring the Agent + Tools",
        "bullets": [
            "Agent Builder creates the agent and 5 tools via REST API.",
            "4 read tools + 1 write tool (save-knowledge-fact).",
            "The MCP endpoint goes live — zero custom server code written.",
            "That URL at the bottom is what Kiro will connect to.",
        ],
        "commentary": (
            "This is the part people expect to be hard and isn't: there's no bespoke MCP server "
            "to write and maintain. Agent Builder exposes the five tools — four to read memory, "
            "one to write it — behind a single MCP endpoint over standard REST. Any MCP-aware "
            "client, Kiro today and your IDE tomorrow, speaks to it without a line of glue code."
        ),
    },
    "live-build: seed": {
        "headline": "Loading 2 Weeks of History",
        "bullets": [
            "68 docs seeded: 10 dev sessions, 18 knowledge facts, 40 conversation turns.",
            "The real decisions: integer cents, Stripe idempotency, JWT auth, Aurora.",
            "sess-005 cents, sess-002 JWT, sess-004 refund policy, sess-007 idempotency.",
            "This is the institutional memory the amnesiac never had.",
        ],
        "commentary": (
            "In real use, agents write to this index as they work — decisions, bug fixes, "
            "conventions — via the same save-knowledge-fact tool you'll see in Act 2. Here we "
            "fast-forward two weeks so the demo lands in one sitting. These 18 facts "
            "are exactly the decisions Act 1 got wrong — money as integer cents because floats "
            "caused a real production bug, the refund cap and 90-day window, the idempotency "
            "convention. This is the difference between a smart agent and YOUR team's agent."
        ),
    },
    "wire: open mcp.json in vi": {
        "headline": "Wiring Kiro to Elastic",
        "bullets": [
            "One JSON block in ~/.kiro/settings/mcp.json — that's the entire integration.",
            "The URL is the Agent Builder MCP endpoint; headers carry the auth.",
            "No custom MCP server. Agent Builder IS the MCP server.",
            "Restart Kiro and all 5 tools appear.",
        ],
        "commentary": (
            "The integration cost is one JSON block — a URL and an auth header — not a service "
            "you have to deploy and operate. Because memory is exposed over MCP, the same "
            "endpoint drops into any compliant client, so this isn't a Kiro-specific hack. You "
            "are wiring a brain into the agent, and the wiring is a config edit."
        ),
    },
    "wire: start kiro": {
        "headline": "Kiro Restarts with Memory",
        "bullets": [
            "kiro-cli picks up the new MCP config on startup.",
            "The 5 Elastic tools are now available — still no code written.",
            "Same CLI, same interface — one JSON block changed everything.",
        ],
        "commentary": (
            "Same binary, same prompt window — the only thing that changed is that the agent now "
            "has hands that can reach into the team's memory. Nothing about the developer's "
            "workflow changed; they didn't learn a new tool. The capability arrived through "
            "configuration, which is exactly why this scales past a single power user."
        ),
    },
    "wire: restart Kiro, select agent": {
        "headline": "Selecting the Memory Agent",
        "bullets": [
            "/agent switches Kiro to the checkout-memory configuration.",
            "Same refund prompt is about to run — verbatim, word for word.",
            "Watch the FIRST thing Kiro does before writing any code.",
        ],
        "commentary": (
            "We're about to run a controlled experiment: identical prompt, identical codebase, "
            "the one variable being whether the agent can see the team's memory. Keep your eye "
            "on the agent's first move. In Act 1 it started typing code immediately; watch what "
            "it reaches for first now."
        ),
    },
    "Act 2 — refund ask (memory)": {
        "headline": "Same Prompt. Different First Move.",
        "bullets": [
            "Verbatim refund prompt — byte-for-byte identical to Act 1.",
            "First move: search-knowledge-facts, NOT code.",
            "It's asking: what has this team already decided about refunds?",
            "That single call is the entire difference between Act 1 and Act 2.",
        ],
        "commentary": (
            "This is the whole talk in one frame: the agent's instinct flips from 'start writing' "
            "to 'first, check what we already know.' It queries memory before touching a "
            "keystroke of implementation — the same reflex a good senior engineer has when they "
            "join a new area of the codebase. Intelligence didn't change; access to context did."
        ),
    },
    "Act 2 — plan (team decisions)": {
        "headline": "Citing the Team's Decisions",
        "bullets": [
            "Reads the codebase, then surfaces what memory returned.",
            "sess-004-fact-2: partial refunds, cumulative cap, 90-day window.",
            "sess-005-fact-0: integer cents, dollar string only at the boundary.",
            "sess-007-fact-0: Stripe idempotency key format.",
            "Every rule Act 1 missed, retrieved before a line is written.",
        ],
        "commentary": (
            "Every policy the amnesiac agent violated, this one retrieves up front and cites by "
            "session ID — the cap, the window, the cents convention, the idempotency format. "
            "This is provenance, not a guess: the agent can tell you not just what the rule is "
            "but where the team decided it and why. That traceability is what turns an AI "
            "suggestion into something a reviewer can actually trust."
        ),
    },
    "Act 2 — write models.py": {
        "headline": "models.py — The Refund Table",
        "bullets": [
            "Adds the Refund SQLAlchemy model matching the Aurora schema.",
            "created_at column — required for the 90-day window check.",
            "Idempotency key as a UNIQUE column — enforced at the DB level.",
            "Schema reflects the policy, not just the request.",
        ],
        "commentary": (
            "The data model itself encodes the team's rules: a created_at to enforce the 90-day "
            "window and a unique constraint on the idempotency key so a duplicate can't slip "
            "through even if application logic fails. The agent is designing for the decisions in "
            "memory, not just satisfying the literal ask. That's the difference between code that "
            "works in the demo and code that survives production."
        ),
    },
    "Act 2 — write payments.py": {
        "headline": "payments.py — The Stripe Call",
        "bullets": [
            "Adds create_refund() reusing the existing _with_backoff retry helper.",
            "Idempotency key passed through — Stripe deduplicates retries.",
            "Mirrors the exact pattern of create_charge() already in the file.",
            "Consistent with the codebase, not just correct in isolation.",
        ],
        "commentary": (
            "Without the idempotency key, a network retry on a refund means you pay the customer "
            "twice — the kind of bug that shows up as a chargeback, not a stack trace. The agent "
            "reuses the team's existing backoff helper and matches the charge path exactly, so "
            "the new code reads like the people who wrote the rest of the file wrote it. Memory "
            "drives consistency, and consistency is what makes a codebase maintainable."
        ),
    },
    "Act 2 — write checkout.py": {
        "headline": "checkout.py — The Endpoint",
        "bullets": [
            "90-day window check. Cumulative refund cap. All policy rules enforced.",
            "dollars_to_cents() at the boundary — integer cents to Stripe and the DB.",
            "JWT auth via get_current_user — same guard as every other route.",
            "None of this existed in Act 1. All of it came from memory.",
        ],
        "commentary": (
            "Here's the payoff: the endpoint enforces the 90-day window, the cumulative cap, "
            "integer-cents math, and JWT auth — the entire list of things a human had to hand-fix "
            "in Act 1 — correct on the first pass. Nobody re-explained any of it; the agent "
            "pulled it from the team's memory. This is what 'shifting correctness left' actually "
            "looks like: the rules are applied at authoring time, not caught in review."
        ),
    },
    "Act 2 — verify + summary": {
        "headline": "Verification + Audit Trail",
        "bullets": [
            "Re-reads all three changed files to confirm correctness.",
            "Cites the session IDs behind each decision in its summary.",
            "Memory-aware means code WITH provenance, not just code.",
            "A reviewer can trace every choice back to a recorded decision.",
        ],
        "commentary": (
            "The agent doesn't just hand you a diff — it tells you which past decision justifies "
            "each choice, by session ID. For a reviewer that's gold: instead of relitigating "
            "whether refunds should be capped, you confirm the code matches a decision the team "
            "already ratified. Provenance turns code review from archaeology into verification."
        ),
    },
    "Act 2 — write beat (fix idempotency key)": {
        "headline": "A New Decision Just Happened",
        "bullets": [
            "Flaw spotted: amount-based key means two $5 refunds on one order collide.",
            "Fix: refund-{uuid4} — a per-attempt UUID. One-line change.",
            "This is a brand-new decision, made live, that memory didn't have yet.",
            "Now capture it so the next engineer never rediscovers it.",
        ],
        "commentary": (
            "Memory isn't a static seed file — here the team makes a genuinely new decision on "
            "stage: switch from an amount-based key to a per-attempt UUID so two equal partial "
            "refunds can't collide. The point isn't the one-line fix, it's what happens next. A "
            "lesson learned the hard way only has value if it's written down before everyone "
            "forgets the context that produced it."
        ),
    },
    "response: Act 2 — write beat (save UUID rule)": {
        "headline": "Writing to Memory",
        "bullets": [
            "save-knowledge-fact writes the UUID convention back to Elasticsearch.",
            "Fact ID: Wn9ktp4BniyjIMohO9V5 — this is exactly what Act 3 will retrieve.",
            "The agent isn't just consuming memory now — it's creating it.",
            "The write→read loop is the whole demo. This is the write half.",
        ],
        "commentary": (
            "This is the moment memory becomes a living system instead of a read-only archive: "
            "the agent writes the new convention back through save-knowledge-fact, no human "
            "transcription required. The decision is captured in the same instant it's made, "
            "while the reasoning is still fresh. Remember fact ID Wn9ktp4B — Act 3 is going to "
            "pull it back cold."
        ),
    },
    "Act 2 — session exit": {
        "headline": "Act 2 Ends — Knowledge Persisted",
        "bullets": [
            "checkout-memory Kiro exits — but this time something survives.",
            "Fact Wn9ktp4B is committed to the knowledge-facts index.",
            "It outlives the session, the laptop, and the chat window.",
            "Act 3 proves any teammate can retrieve it.",
        ],
        "commentary": (
            "Contrast this with the end of Act 1, where everything vanished. Here the session "
            "closes but the decision persists in Elasticsearch, decoupled from this chat, this "
            "machine, and this person. The agent's learning is now a team asset instead of one "
            "developer's scrollback — which is the entire reason to build a memory layer."
        ),
    },
    "Act 3 — fresh session, select agent": {
        "headline": "New Session. New Engineer.",
        "bullets": [
            "Kiro restarted — the Act 2 session history is completely gone.",
            "But the knowledge facts are still sitting in Elasticsearch.",
            "Same /agent select — this is the teammate picking up cold.",
            "Different context window, shared memory.",
        ],
        "commentary": (
            "We've thrown away the conversation — fresh session, empty context window — to "
            "simulate a different engineer opening the project for the first time. They have none "
            "of Act 2's chat history, the same way a real teammate wouldn't. The only thing they "
            "share is the durable memory in Elasticsearch, which is the entire point."
        ),
    },
    "Act 3 — read-back (teammate)": {
        "headline": "The Question Every Teammate Asks",
        "bullets": [
            "'What's our convention for idempotency keys on refunds?'",
            "Semantic search hits Wn9ktp4B — the fact saved 2 minutes ago in Act 2.",
            "No Slack archaeology, no PR comment hunt, no pinging the one person who knows.",
            "Tribal knowledge, made queryable.",
        ],
        "commentary": (
            "This is the question that normally costs an hour: someone pings Slack, digs through "
            "old PRs, or interrupts the one engineer who remembers. Instead it's a single query "
            "that hits the fact written two minutes ago — and it matches on meaning, so the "
            "teammate didn't have to phrase it the way it was stored. Tribal knowledge stops "
            "being something you have to know who to ask."
        ),
    },
    "Act 3 — answer": {
        "headline": "Memory Is the Answer",
        "bullets": [
            "Answer: refund-{uuid4} — per-attempt UUID, not order+amount.",
            "It explains WHY: two equal partial refunds would otherwise collide.",
            "Write (Act 2) → read (Act 3) loop, closed live, in minutes.",
            "Stateless to stateful. That's the talk — repo + blog in the CTA.",
        ],
        "commentary": (
            "The loop closes: a decision made and saved in Act 2 is retrieved, with its rationale, "
            "by a fresh session in Act 3 — write then read, proven live. That's the leap from "
            "stateless to stateful, and it's three Elasticsearch indices plus an MCP endpoint, "
            "not a research project. The repo and blog in the CTA give you everything you need to "
            "build the same thing against your own stack this week."
        ),
        "queries": [
            "FROM knowledge-facts",
            "| WHERE session_id == \"sess-004\"",
            "| KEEP fact, category,",
            "|   importance, session_id",
            "",
            "FROM knowledge-facts",
            "| WHERE session_id == \"sess-007\"",
            "| KEEP fact, category,",
            "|   importance, session_id",
        ],
    },
}
