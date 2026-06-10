---
type: final
title: "AWS Summit NYC 2026 — Demo Capture Run-Book"
status: pre-recording
category: content
priority: high
created: 2026-06-10
updated: 2026-06-10
tags: [aws-summit-2026, demo, runbook, kiro, capture, elastic-bedrock-memory]
---

# AWS Summit NYC 2026 — Demo Capture Run-Book

**The single source of truth for what gets typed, run, and captured.** The Navattic
shot sheet is a recording-formatted view of this; the practice guide is the stage
narration over it. If they disagree, this file wins.

**Narrative spine:** one task — *add a refund endpoint* — carried across the whole
hands-on portion. Built **wrong** by an amnesiac Kiro (Act 1), then **right** by a
memory-wired Kiro (Act 2), with the memory system **built live** in between.

**Total hands-on runtime:** ~30 min of live screen content (segments 2–6 of the talk).

---

## How to use this file

- Each segment lists: **state required**, **exact prompts/commands**, **target
  output**, and **capture notes**.
- The "amnesiac" slips in Act 1 are non-deterministic. This file tells you how to
  **elicit** them and how to **fall back** to a known-good capture if live Kiro
  behaves differently. It's recorded footage — re-run until the take is right.
- Reference implementations of both the **wrong** and **correct** refund code live
  in `demo_scripts/reference/`. Use them to verify a take captured the right slips,
  or paste them in if a live run underperforms.

---

## The codebase under test: `~/repos/checkout-service-demo`

A real, minimal FastAPI checkout service. Baseline is committed — reset between
takes with `git -C ~/repos/checkout-service-demo checkout .`

What it already contains (the patterns Act 1 violates and Act 2 mirrors):

| File | Establishes |
|------|-------------|
| `app/money.py` | Money is **integer cents**; `dollars_to_cents` takes str/Decimal, never float |
| `app/models.py` | `amount_cents: int`; `WebhookEvent` unique ledger = idempotency pattern |
| `app/auth.py` | `get_current_user` JWT dependency (Okta JWKS) |
| `app/payments.py` | `create_charge(idempotency_key=…)` wrapped in `_with_backoff`; **no `create_refund`** |
| `app/routers/checkout.py` | Every route is `Depends(get_current_user)`, cents throughout |
| `app/main.py` | `# Refund routes: not implemented yet.` |

**By design there is NO decisions-log file.** The code shows *what* (cents, JWT) but
never *why*, and the refund policy (90-day window, partial cap) exists in neither
code nor memory yet. Memory's exclusive claim on the *reasoning* is what makes Act 2
land instead of looking like a grep.

---

## Pre-recording setup (once)

```bash
cd ~/repos/elastic-bedrock-memory

# 1. Clean Elastic state, then we'll build it live on camera in Segment 3.
python3 setup/demo-setup.py --nuclear   # deletes + recreates indices, full rebuild
# (For the Segment 3 capture you'll re-run the INDIVIDUAL scripts on camera against
#  a clean project — see Segment 3. --nuclear here just guarantees a known baseline.)

# 2. Reset the codebase to baseline.
git -C ~/repos/checkout-service-demo checkout .

# 3. Confirm fonts 16px+, window 1920×1080, dock/menubar hidden.
```

### State matrix — what must be true per segment

| Segment | Elastic memory | Kiro agent | mcp.json | checkout-service-demo |
|---------|----------------|-----------|----------|----------------------|
| 2 — Act 1 amnesia | not wired to Kiro | **stock** (default) | **no** elastic-memory | baseline |
| 3 — live-build | building on camera | n/a | n/a | n/a |
| 4 — wire memory | populated | switching to checkout-memory | **adding** elastic-memory | baseline |
| 5 — Act 2 memory | populated | **checkout-memory** | elastic-memory present | baseline (reset after Act 1) |
| 6 — cross-session | populated + 1 saved fact | checkout-memory | present | n/a |

> Record in story order if you can. If you record out of order, the only thing that
> matters is that the row above is true at capture time. **Critical:** reset the
> codebase to baseline before Act 2 so refunds don't already exist from Act 1.

---

# SEGMENT 2 — Act 1: Amnesia (refunds, built wrong) · ~6 min

**State:** Kiro launched from `~/repos/checkout-service-demo`, **stock agent**, no
elastic-memory in mcp.json. Kiro can read/grep the code but has zero access to the
team's decision history.

### (Optional, ~20s) Within-session memory nod
> Type: `I'm back on the checkout service. We're adding refunds today.`
> Kiro acknowledges. **Say:** "Kiro remembers what I tell it *in this session*. That's
> working memory, and it's fine. Watch what it doesn't have."
> *(Cut this beat if Act 1 runs long — it's a nicety, not load-bearing.)*

### The ask (verbatim — identical to Act 2)

```
I need to add refunds to the checkout service. Add a POST endpoint that lets a
customer request a refund on an order — support partial refunds where they can pass
a dollar amount to refund. Wire it up to Stripe.
```

**Why this prompt:** it forces *new* reasoning — a dollar-amount input (float
temptation), a brand-new Stripe call (idempotency slip), a fresh route (JWT slip),
and partial-amount math (cents + double-refund slip). The house rules aren't carried
over because the agent reasons from general priors, not the team's history.

### Target slips (need ~3 of 4 to land the point)

| # | Slip | Reference to violated decision |
|---|------|-------------------------------|
| 1 | Accepts a **float** dollar amount and/or does float math → reintroduces the 1-cent bug | money = integer cents (sess-005) |
| 2 | `stripe.Refund.create(...)` with **no `idempotency_key`** (and no backoff) | Stripe idempotency + backoff (sess-004/007) |
| 3 | New `/refund` route has **no `Depends(get_current_user)`** | JWT on every route (sess-002) |
| 4 | **No guard** against double-refund / refunding more than the order total | idempotency ledger (sess-004) |

### Eliciting the slips (if Kiro behaves "too well")
- Keep the prompt fast and direct — don't tell it to "review the codebase first."
- The phrase "pass a dollar amount to refund" is the float lure. Keep it.
- If it still nails everything, add a follow-up: `Keep it simple, just get the happy
  path working.` — agents cutting corners skip auth and idempotency first.
- Worst case (it gets 1–2 right): still fine. One reintroduced cents bug + one missing
  auth is enough to carry "I had to remember this *for* it."
- Verify the take against `demo_scripts/reference/refunds-amnesiac.py`.

### The correction beats (Jeff types these as he catches each slip)

1. `Hold on — we store money as integer cents, never floats. We had a 1-cent rounding
   bug from exactly this kind of math two weeks ago. Use the money helpers.`
2. `That Stripe refund needs an idempotency key like our charge path does, or a retry
   double-refunds the customer.`
3. `This route isn't authenticated — every other route uses get_current_user.`
4. *(if applicable)* `And guard against double refunds and refunding more than the
   order total.`

Kiro fixes each — **but only because you remembered.** That's the whole point.

### Breaking point (to the room, ~45–60s — let it land)
> "Every one of those corrections is something my team *already decided*. The cents
> rule — we paid for that with a production bug. The idempotency pattern, the auth
> convention. It's written down in past sessions, it's in my head, it's in a
> teammate's brain. Kiro had none of it. And tomorrow, new session, I do this all
> over again. That's the amnesia tax — every session, every teammate, forever."

### Capture notes
- Capture the wrong code streaming in (compress to ~20–30s in Navattic).
- Capture each correction → Kiro's fix at near-real speed (these are the rich beats).
- Hold on the final "fixed by hand" diff before the breaking-point line.

---

# SEGMENT 3 — Live-build the memory system · ~10 min

**State:** a **freshly reset** Elastic project (run `--nuclear` before this take so the
scripts show *clean creation*, not "already exists"). Terminal + browser (Kibana).

**Frame:** "Kiro's amnesia isn't Kiro's fault — it has no memory store. So let me build
one. Live. In under ten minutes."

### Command sequence (run on camera, in order)

```bash
cd ~/repos/elastic-bedrock-memory

# 1. Three indices, each with a semantic_text field.
python3 setup/create-indices.py
```
> **Show the mapping.** "Three indices: conversation history, knowledge facts, session
> metadata. Look at this one field — `semantic_text`. That *is* the embedding pipeline.
> Jina v5 vectorizes every document at ingest. No pipeline to build, no model to host."

```bash
# 2. The Agent Builder agent + its tools, created via the REST API.
python3 setup/create-agent.py
```
> "This creates the agent and its tools through Agent Builder's API — semantic search
> tools, ES|QL tools for structured recall, and a write tool. No custom server. Agent
> Builder *is* the MCP server."

```bash
# 3. Two weeks of the team's history, loading in.
python3 demo-data/seed.py
```
> "In a real workflow every session writes here automatically. To save us two weeks,
> I've got ten realistic sessions — decisions, bug fixes, the works — loading now.
> 67 documents." *(Show the doc counts.)*

### Kibana glance (browser)
- Agent Builder → the `checkout-service-memory` agent now exists with its tools.
- Open one index's mapping in Dev Tools or Index Management → point at `semantic_text`.
> "Built. A complete memory system — indices, embeddings, an agent, tools — in the time
> it took to say it."

### Capture notes
- This segment flexes: if pacing runs hot, cut the Kibana glance; if cold, expand the
  mapping explanation. It's your buffer segment.
- Pre-run once to confirm clean output and capture script run-times; compress long
  pauses in Navattic.

---

# SEGMENT 4 — Wire memory to Kiro · ~3 min

**State:** mcp.json does NOT yet have elastic-memory (it was removed in `--prep`, or
never added). Memory system is populated (Segment 3 done).

```bash
# Show mcp.json BEFORE — no elastic-memory block.
# Then:
python3 setup/demo-setup.py --add-mcp
# Show mcp.json AFTER — elastic-memory block: url → /api/agent_builder/mcp, 3 headers.
```

- Open `~/.kiro/agents/checkout-memory.json` — the **Skill**. Point at the prompt
  ("before answering project questions, check memory first") and the
  `@elastic-memory/*` tools and `"model": null` (auto = runs on Bedrock).
- Restart Kiro → `/agent` → select **checkout-memory (Global)**.

> "Two files. An MCP config — a URL and three headers, pointing at Agent Builder's
> native endpoint. And a Skill that tells Kiro: check memory before you answer.
> That's the entire integration."

---

# SEGMENT 5 — Act 2: Memory (refunds, built right) · ~7 min

**State:** checkout-memory agent active, elastic-memory wired, **fresh Kiro session**,
codebase **reset to baseline** (`git checkout .`). Run from `~/repos/checkout-service-demo`.

### The ask (VERBATIM SAME as Act 1 — this is the payoff)

```
I need to add refunds to the checkout service. Add a POST endpoint that lets a
customer request a refund on an order — support partial refunds where they can pass
a dollar amount to refund. Wire it up to Stripe.
```

### Target behavior
1. **Before writing code**, Kiro calls `search-knowledge-facts` (the Skill kicks in).
   nlQuery resembles: *"money handling, payments, Stripe, refund-related decisions."*
   → retrieves: integer cents (sess-005), Stripe idempotency (sess-004), retry/backoff
   (sess-007), JWT auth (sess-002). **This tool call is the money shot — let it breathe.**
2. Writes the refund route **correctly, first pass**, and **cites sources**: "Based on
   the decision in session 5, amounts are integer cents…"; "matching the idempotency
   pattern from session 4…". Target output: `demo_scripts/reference/refunds-correct.py`.
3. **Side-by-side:** put Act 1's hand-corrected mess next to this (you have multiple
   screens). Same prompt. One fought you; one knew the house rules.

> "Same prompt. Word for word. The only thing that changed is that Kiro can see what we
> already decided — so it just *does it right*. And it tells me where each rule came from."

### Go deeper (this is the "restart and go longer" beat)
- If Kiro carried over the backoff/retry without being asked: **call it out.** "Notice
  it applied the retry-with-backoff from our charge path to the refund call — I never
  asked. It pattern-matched our own conventions."
- Introduce the **new** decision:
  > `Now enforce the refund rules: partial refunds up to the original charge minus any
  > prior refunds, and only within 90 days of the order. Then save that policy to memory.`
- `save-knowledge-fact` fires. Watch the tool call (fact, category, project, importance).
  > "That decision didn't exist anywhere a minute ago — not in the code, not in memory.
  > Now it's in Elasticsearch. Kiro just wrote to the team's memory."

### Capture notes
- Capture the `search-knowledge-facts` call → retrieved facts → code generation, with
  citations visible. This is the most important capture in the whole talk.
- Capture the `save-knowledge-fact` tool call with its inputs expanded.

---

# SEGMENT 6 — Act 3: Cross-session + under the hood · ~4 min

**State:** post-Act-2 (the refund-policy fact is now saved). checkout-memory agent.

### Cross-session / teammate read-back (~90s)
- **New Kiro session** (frame it: "now I'm a teammate on a different machine, brand new
  context"). Ask:
  ```
  What's our refund policy — can customers get partial refunds, and is there a time limit?
  ```
- `search-knowledge-facts` fires → returns the 90-day / partial-cap fact saved in Act 2.
> "Brand new session. A decision made minutes ago by a different developer — retrieved
> instantly. That's cross-session, cross-machine, cross-team. The memory isn't on my
> laptop. It's in Elasticsearch."

### Kibana — the audit trail (~2 min)
- Agent Builder → **Conversations** tab → open the recorded session, expand the tool
  calls (the query sent, the documents returned).
> "Every agent call, every tool, every document retrieved — logged. Not a black box.
> This is the governance and audit story for free."

*(Optional, if time: show the 5 tools on the agent, or the save-knowledge-fact workflow
type. But don't re-explain the agent — Segment 3 already built it.)*

---

## Reset procedures between takes

| Retake | Reset |
|--------|-------|
| Act 1 | `git -C ~/repos/checkout-service-demo checkout .`; fresh stock Kiro session |
| Live-build | `python3 setup/demo-setup.py --nuclear` (clean project again) |
| Wire memory | `python3 setup/demo-setup.py --prep` (removes elastic-memory), restart Kiro |
| Act 2 | `git checkout .` in codebase; `--reset` if a stray fact was saved; fresh session |
| Act 3 read-back | fresh Kiro session (do NOT reuse the Act 2 session) |
| Full reset | `python3 setup/demo-setup.py --reset` + `git checkout .` in codebase |

## Open risk carried from HANDOFF
The `save-knowledge-fact` write path (Workflow `save-knowledge-fact-3`) was created with
`valid: False` in Kibana's API response. **Verify it fires and writes end-to-end before
recording Segment 5's write beat.** If it doesn't: fall back to the local MCP sidecar
(`mcp-sidecar/save-fact-server.py`) for the write, or stage the write beat as "Kiro
proposes the save; here it is landing in Kibana" using a direct ES write. See HANDOFF
"OPEN ISSUE" section.
