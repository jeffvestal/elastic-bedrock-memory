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
  in `../reference/`. Use them to verify a take captured the right slips,
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

## Recording flow — three states, set once each, recorded in story order

The demo needs three different states. Record in story order and you set each one
exactly once. `--prep` only edits `mcp.json` now — it does **not** touch the codebase.

> ⚠️ Do **not** run `--nuclear` as a "baseline" — it *builds + seeds* everything,
> which makes the live-build capture (Phase 2) show "already exists" instead of
> creation. Use the phases below.

```bash
cd ~/repos/elastic-bedrock-memory
# Confirm fonts 16px+, window 1920×1080, dock/menubar hidden.
```

### ⚡ Just get me to Act 1 (don't care where I am)

```bash
cd ~/repos/elastic-bedrock-memory
python3 setup/demo-setup.py --prep                 # a — strip memory out of Kiro
git -C ~/repos/checkout-service-demo checkout .     # b — clean the codebase
# c — restart Kiro, pick the DEFAULT agent (NOT checkout-memory)
```
Now start Act 1. Any memory you already built stays put — Act 1 just can't see it, which is the point. (You only need `--clean` when you're ready to *film the live-build*.)

---

**Phase 1 — Act 1 (amnesia).** No memory wired.
```bash
python3 setup/demo-setup.py --prep                 # removes elastic-memory from mcp.json
git -C ~/repos/checkout-service-demo checkout .     # codebase baseline
# Restart Kiro; select the STOCK/default agent (NOT checkout-memory).
# Verify: Kiro's /mcp list shows NO elastic-memory and no memory tools.
```
Record Act 1. (Whether the indices hold data is irrelevant — memory isn't wired.)

**Phase 2 — Segment 3 (live-build).** Empty Elastic so the scripts show real creation.
```bash
python3 setup/demo-setup.py --clean                # deletes indices + agent/tools/skill (keeps the workflow)
```
Then record on camera: `create-indices.py` → `create-agent.py` → `seed.py`. Memory is now built + populated.

**Phase 3 — Wire + Act 2 + Act 3.** Memory wired.
```bash
python3 setup/demo-setup.py --add-mcp              # adds elastic-memory back to mcp.json
git -C ~/repos/checkout-service-demo checkout .     # baseline, so refunds don't already exist from Act 1
# Restart Kiro; select the checkout-memory agent.
```
Record Segment 4 (the mcp.json before/after is automatic — Phase 1's `--prep` is the
"before", this `--add-mcp` is the "after"), then Act 2, then Act 3.

> **Dry run vs recording:** for a quick end-to-end *test* you don't need `--clean` —
> already-built memory is fine; just `--prep` for Act 1, then `--add-mcp` + the
> checkout-memory agent for Act 2/3. `--clean` exists only to make the live-build
> *capture* show creation.

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

# SEGMENT 2 — Act 1: Amnesia (refunds built clean — but policy-blind) · ~6 min

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

**What actually happens (verified live):** with the repo in front of it, a capable
agent gets the *code patterns* right by reading them — integer cents, Stripe
idempotency + backoff, JWT + ownership, a Refund model, async session. **Don't expect
it to write buggy code — it won't, and that's fine.** The gaps are the things that
live only in team decisions, never in the code.

### What it gets right vs. the gaps (the gaps are the whole point)

| ✅ Right — from *reading the repo* | ❌ Missing — lives only in *team memory* |
|---|---|
| integer cents (`dollars_to_cents`) | **No cumulative cap** → it may add a naive per-call `amount > order total` guard, but never tallies prior refunds, so the order can be drained over repeated calls |
| Stripe idempotency + `_with_backoff` | **No 90-day window** — no time check at all |
| JWT + ownership check | **Amount-based idempotency key** (`{order_id}-refund-{amount_cents}`) → two equal partial refunds collide; Stripe silently drops the 2nd |
| Refund model, async session | (and it states the key choice *confidently* in a comment — wrong, but sure of itself) |

You don't need to "elicit" anything — a good agent exhibits all three gaps naturally.
Verify the take against `../reference/refunds-amnesiac.py`.

### The correction beats (Jeff feeds the policy from his own memory)

1. `Even with that cap, you never tally prior refunds — I can refund the full amount,
   then do it again. Our policy is cumulative: capped at the original charge minus
   everything already refunded.`
2. `And there's no time limit. We only allow refunds within 90 days; older ones go to
   manager approval — return a 422.`
3. `That idempotency key is order-id plus amount — two $10 refunds on one order would
   collide and the second silently wouldn't go through. Keys have to be per-attempt.`

Kiro fixes each — **but only because *you* remembered the team's decisions.** Note the
shape: it's not that Kiro is dumb. It wrote good code. It just couldn't see the policy.

### Breaking point (to the room, ~45–60s — let it land)
> "Look at what happened. Kiro wrote clean code — cents, idempotency, auth — because it
> could read the codebase. But it had no idea about our refund *policy*: it'd refund more
> than you paid, with no time limit. And it shipped an idempotency bug we'd catch in
> review. None of that is in the code — it's in decisions my team made, in past sessions,
> in my head. Kiro couldn't see any of it. New session tomorrow? Same blind spots, again."

### Capture notes
- Capture the clean code streaming in (compress to ~20–30s).
- Capture each correction → Kiro's fix at near-real speed (the rich beats).
- Hold on the over-refund gap + the amount-based key line before the breaking point —
  those two are the most visceral "it couldn't have known that."

---

# SEGMENT 3 — Live-build the memory system · ~10 min

**State:** an **empty** Elastic project (run `--clean` before this take so the
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
   nlQuery resembles: *"refund policy, refund rules, payment decisions."* → retrieves the
   **refund policy** (partial cap + 90-day window, sess-004) alongside the payment
   patterns. **This tool call is the money shot — let it breathe.**
2. Writes the refund route with the **policy baked in** — caps the amount at original
   minus prior refunds, enforces the 90-day window (422 otherwise) — and **cites the
   source**: "Per the refund policy from session 4…". Target: `reference/refunds-correct.py`.
   (It gets cents/idempotency/JWT right too — but so did Act 1; the *visible* win is the policy.)
3. **Side-by-side:** Act 1 (refunds more than the order, no window, amount-keyed) next to
   Act 2 (capped, windowed, cites the decision). Same prompt.

> "Same prompt. The amnesiac build would refund more than the order, forever. This one
> knows our policy — capped, 90-day window — because it read a decision we made weeks ago.
> And it tells me which session it came from."

### Go deeper — turn Act 1's bug into memory (the write beat)
The policy was *recalled* (already in memory). Now create something **new**: the fix for
the idempotency-key bug Act 1 shipped.
  > `One more thing — the refund idempotency key can't be amount-based; two equal partial
  > refunds would collide. Use a per-attempt UUID (refund-{uuid}). Save that as a decision
  > so we never repeat it.`
- `save-knowledge-fact` fires. Watch the tool call (fact, category, project, importance).
  > "That bug the amnesiac version shipped a minute ago? I just turned the fix into team
  > memory. Next session — mine or a teammate's — the agent retrieves it and never makes
  > that mistake again."

### Capture notes
- Capture the `search-knowledge-facts` call → retrieved facts → code generation, with
  citations visible. This is the most important capture in the whole talk.
- Capture the `save-knowledge-fact` tool call with its inputs expanded.

---

# SEGMENT 6 — Act 3: Cross-session + under the hood · ~4 min

**State:** post-Act-2 (the idempotency-key rule is now saved). checkout-memory agent.

### Cross-session / teammate read-back (~90s)
- **New Kiro session**, then `/agent` → **checkout-memory** (a fresh session defaults to
  stock Kiro — re-select the agent or the memory tools won't fire). Frame it: "now I'm a
  teammate on a different machine, brand new context, about to add another Stripe write". Ask:
  ```
  What's our convention for idempotency keys on refunds?
  ```
- `search-knowledge-facts` fires → returns the per-attempt-UUID rule **saved in Act 2**.
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
| Live-build | `python3 setup/demo-setup.py --clean` (empty Elastic again) |
| Wire memory | `python3 setup/demo-setup.py --prep` (removes elastic-memory), restart Kiro |
| Act 2 | `git checkout .` in codebase; `--reset` if a stray fact was saved; fresh session |
| Act 3 read-back | fresh Kiro session (do NOT reuse the Act 2 session) |
| Full reset | `python3 setup/demo-setup.py --reset` + `git checkout .` in codebase |

## Write path — RESOLVED (2026-06-11)
The `save-knowledge-fact` write beat works end-to-end (agent → tool → workflow → ES),
verified via the Agent Builder converse API: the agent passed a real `fact` and the doc
landed fully populated with an ISO `timestamp`.

**The fix that mattered (Elastic 9.5 serverless gotcha):** workflow `inputs` MUST be
nested **under the manual trigger**, not declared top-level. Only then does Agent Builder
derive the workflow-tool parameter schema, so the agent has params to fill. Top-level
`inputs:` parse to `definition.inputs=null`, the tool exposes `properties: {}`, and the
agent writes empty docs. The write step uses `elasticsearch.index` (document block);
`timestamp` is `{{ execution.startedAt | date: '%Y-%m-%dT%H:%M:%SZ' }}` (raw renders as a
non-ISO JS date string ES rejects). Both are baked into `setup/validate-write-path.py`.

**Before recording:** restart Kiro so it reloads the re-derived tool, then confirm the
write beat fires and `knowledge-facts` goes 18 → 19.
