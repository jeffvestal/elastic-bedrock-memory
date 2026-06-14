---
type: final
title: "AWS Summit NYC 2026 — Navattic Shot Sheet"
status: pre-recording
category: content
priority: high
created: 2026-06-02
updated: 2026-06-11
tags: [aws-summit-2026, navattic, demo, elastic-bedrock-memory, shot-sheet]
---

# AWS Summit NYC 2026 — Navattic Shot Sheet

**Recording target:** Click-through demo for "From Stateless to Stateful" session
**Source of truth:** `demo_scripts/aws-summit-2026-demo-runbook.md` (run-book wins on all conflicts)
**Repo:** `github.com/jeffvestal/elastic-bedrock-memory`
**Total shots:** ~35 steps across 8 scenes
**Demo runtime:** ~12 minutes in Navattic

**Narrative spine:** One task — *add a refund endpoint* — built **clean but policy-blind** without memory (Act 1), the memory system **built live** in front of the audience, **wired** to Kiro, then the same task built **right** with memory (Act 2). Cross-session read-back and Kibana audit trail close it out.

### Kibana (Agent Builder):
https://bedrock-memory-demo-e86908.kb.us-east-1.aws.elastic.cloud

### Kiro:
Kiro launched from `~/repos/checkout-service-demo`. For Act 1 (Scene 2): stock agent, no elastic-memory in mcp.json. For Act 2 (Scene 5): checkout-memory agent active, elastic-memory wired.

---

## Pre-Recording Setup

Follow the state matrix in the run-book exactly. Abbreviated here for reference:

```bash
cd ~/repos/elastic-bedrock-memory
# Per-phase state — see run-book "Recording flow" section:
#   Act 1:        python3 setup/demo-setup.py --prep      (+ stock agent)
#   Live-build:   python3 setup/demo-setup.py --clean     (empty Elastic for the capture)
#   Wire+Act2/3:  python3 setup/demo-setup.py --add-mcp   (+ checkout-memory agent)
git -C ~/repos/checkout-service-demo checkout .           # codebase baseline (before Act 1 and Act 2)
```

See run-book **State matrix** section for what must be true per segment before pressing record. Record in story order when possible — Act 2 requires codebase reset to baseline after Act 1.

### Visual setup (all scenes)
- [ ] Browser open to Kibana Agent Builder — `checkout-service-memory` agent visible
- [ ] Font 16px+ in both Kiro and Kibana
- [ ] Window 1920×1080, menubar/dock hidden
- [ ] Multiple screens ready for side-by-side contrast step in Scene 5

---

## Navattic Notes

- Each row = one Navattic step.
- **Highlight / Hotspot** column = tooltip text, copy-paste ready.
- **Timing** column: `compress` = speed through in Navattic (routine generation, scripted output); `real-time` = let it breathe (dramatic beats — the footage earns its runtime).
- For tool call steps: capture before tool call fires + after response complete. Wire as sequential auto-advance.
- Keep hotspots to 1–2 sentences. Show → name it → say why it matters.

---

## Scene 1 — Architecture (static slide)

**App:** Slide deck | **Captures:** 1

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 1 | Architecture diagram: Kiro → Amazon Bedrock for inference; Kiro → Elastic Agent Builder → Elasticsearch for memory | ✅ Cap 1a | — | **Bedrock arrow:** "Amazon Bedrock — inference runs here. Your AWS account, your model." **Agent Builder arrow:** "Elastic Agent Builder — memory lives here. Native MCP endpoint, no custom server." |

---

## Scene 2 — Act 1: Amnesia (refunds, clean code — policy-blind) · ~6 min

**Purpose:** Show that a capable Kiro reads the repo and gets code patterns right — but is completely blind to the team's refund policy, which lives only in memory.
**State:** Stock Kiro agent. `elastic-memory` NOT in mcp.json. Codebase at baseline (`git checkout .`). Launched from `~/repos/checkout-service-demo/`.
**Note:** Don't wait for Kiro to write buggy code — it won't. The gaps are policy gaps, not code-quality gaps. Verify take against `demo_scripts/reference/refunds-amnesiac.py`.

### What Kiro gets right vs. the gaps

| ✅ Gets right — reads from the repo | ❌ Missing — lives only in team memory |
|---|---|
| Integer cents (`dollars_to_cents`) | No amount cap → can refund more than the order, repeatedly |
| Stripe idempotency + `_with_backoff` | No 90-day window — no time check at all |
| JWT + ownership (`get_current_user`) | Amount-based idempotency key (`{order_id}-refund-{amount_cents}`) → two equal partial refunds collide; Stripe silently drops the 2nd |
| Refund model, async session | (states the key choice confidently in a comment — wrong, but sure of itself) |

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 1 | (Optional) Kiro chat — type: `I'm back on the checkout service. We're adding refunds today.` Kiro acknowledges. | ✅ Cap 2a | compress | Hotspot: "Kiro remembers what you tell it in this session. Working memory — fine. Watch what it doesn't have." |
| 2 | The ask (verbatim): `I need to add refunds to the checkout service. Add a POST endpoint that lets a customer request a refund on an order — support partial refunds where they can pass a dollar amount to refund. Wire it up to Stripe.` | ✅ Cap 2b | compress | Hotspot on prompt: "Same prompt used in Act 2 — word for word. Only one thing changes." |
| 3 | Kiro streams clean code — integer cents, Stripe idempotency + backoff, JWT, Refund model. Amount-based idempotency key (`{order_id}-refund-{amount_cents}`) visible with a confident comment. No cap, no time window. | ✅ Cap 2c | compress | Hotspot on code: "Clean code — it read the repo. But look at the idempotency key. And no cap. No time window." |
| 4 | Jeff types correction 1: `This lets me refund more than the order was — and as many times as I want. Our policy is partial refunds capped at the original charge minus anything already refunded.` Kiro fixes. | ✅ Cap 2d | real-time | Hotspot on correction: "Correction 1. The cap. Our policy — not in the code anywhere. Only in memory." |
| 5 | Jeff types correction 2: `And there's no time limit. We only allow refunds within 90 days; older ones go to manager approval — return a 422.` Kiro fixes. | ✅ Cap 2e | real-time | Hotspot on correction: "Correction 2. The 90-day window. Another decision that lives in past sessions, not in the codebase." |
| 6 | Jeff types correction 3: `That idempotency key is order-id plus amount — two $10 refunds on one order would collide and the second silently wouldn't go through. Keys have to be per-attempt.` Kiro fixes. | ✅ Cap 2f | real-time | Hotspot on correction: "Correction 3. The idempotency bug — it stated this confidently in a comment. Wrong, but sure of itself." |
| 7 | Hold on the corrected diff — all three policy corrections visible | ✅ Cap 2g | real-time | Hotspot on diff: "Every correction fed from memory. Kiro wrote the code. You knew the policy." |
| 8 | Breaking point (Jeff to the room): "Look at what happened. Kiro wrote clean code — cents, idempotency, auth — because it could read the codebase. But it had no idea about our refund policy: it'd refund more than you paid, with no time limit. And it shipped an idempotency bug we'd catch in review. None of that is in the code — it's in decisions my team made, in past sessions, in my head. Kiro couldn't see any of it. New session tomorrow? Same blind spots, again." | ✅ Cap 2h | real-time | No hotspot — let it land. |

---

## Scene 3 — Live-build the memory system · ~10 min

**Purpose:** Build the complete memory system on camera. Audience sees it isn't magic — it's three scripts.
**State:** Empty Elastic project (`--clean` run before this take). Terminal + browser (Kibana). Launched from `~/repos/elastic-bedrock-memory/`.

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 1 | Terminal — run `python3 setup/create-indices.py`. Output shows three indices created. | ✅ Cap 3a | compress | Hotspot on output: "Three indices: conversation history, knowledge facts, session metadata. One script." |
| 2 | Show the index mapping — `semantic_text` field highlighted | ✅ Cap 3b | real-time | Hotspot on `semantic_text`: "This field IS the embedding pipeline. Jina v5 vectorizes every document at ingest. No pipeline to build, no model to host." |
| 3 | Terminal — run `python3 setup/create-agent.py`. Output shows agent + tools created. | ✅ Cap 3c | compress | Hotspot on output: "Agent Builder agent and its tools — created via REST API. Semantic search tools, ES\|QL tools, a write tool. No custom server." |
| 4 | Terminal — run `python3 demo-data/seed.py`. Doc counts stream in. | ✅ Cap 3d | compress | Hotspot on doc counts: "67 documents. Ten sessions of decision history loading now. Two weeks of team memory in seconds." |
| 5 | Kibana — Agent Builder → `checkout-service-memory` agent now exists; tools listed | ✅ Cap 3e | real-time | Hotspot on agent: "Built. Indices, embeddings, an agent, tools — in the time it took to say it. Agent Builder is the MCP server." |

---

## Scene 4 — Wire memory to Kiro · ~3 min

**Purpose:** Show the full wiring: mcp.json before/after, the Kiro Skill, agent select.
**State:** `elastic-memory` NOT yet in mcp.json. Memory system populated (Scene 3 done). Launched from terminal.

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 1 | `~/.kiro/settings/mcp.json` open — elastic-memory block absent | ✅ Cap 4a | compress | Hotspot: "mcp.json — Kiro's MCP server list. No elastic-memory yet." |
| 2 | Terminal — run `python3 setup/demo-setup.py --add-mcp`. Output: "Added 'elastic-memory' to mcp.json". | ✅ Cap 4b | compress | Hotspot on command: "One script. Adds the Agent Builder MCP endpoint to Kiro." |
| 3 | `~/.kiro/settings/mcp.json` open again — elastic-memory block present: `url` → `/api/agent_builder/mcp`, three headers | ✅ Cap 4c | real-time | Hotspot on `"url"` line: "Agent Builder's native MCP endpoint — no custom server to build or operate." Hotspot on headers block: "Three headers. That's the entire integration." |
| 4 | `~/.kiro/agents/checkout-memory.json` open — prompt visible, `@elastic-memory/*` tools listed, `"model": null` | ✅ Cap 4d | real-time | Hotspot on prompt: "A Kiro Skill — before answering project questions, check memory first." Hotspot on `"model": null`: "Auto mode — Kiro runs on Amazon Bedrock. Inference and memory: separate, composable." |
| 5 | Kiro — restart, type `/agent` → picker shows checkout-memory (Global) → select it | ✅ Cap 4e | compress | Hotspot on checkout-memory row: "One Skill. Installed globally. Kiro knows to check Elastic memory before it answers." |

---

## Scene 5 — Act 2: Memory (refunds, built right) · ~7 min

**Purpose:** Same prompt, memory-wired Kiro recalls the refund POLICY first pass with citation. Side-by-side contrast. Write beat turns Act 1's idempotency bug into team memory.
**State:** checkout-memory agent active, elastic-memory wired, fresh Kiro session, codebase **reset to baseline** (`git checkout .`). Launched from `~/repos/checkout-service-demo/`.

### The ask (VERBATIM SAME as Act 1)

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 1 | Kiro chat — type the IDENTICAL prompt: `I need to add refunds to the checkout service. Add a POST endpoint that lets a customer request a refund on an order — support partial refunds where they can pass a dollar amount to refund. Wire it up to Stripe.` | ✅ Cap 5a | compress | Hotspot on prompt: "Same prompt. Word for word. The only thing that changed is memory." |
| 2 | **MONEY SHOT** — `search-knowledge-facts` tool call fires BEFORE any code is written. nlQuery visible (something like: "refund policy, refund rules, payment decisions"). | ✅ Cap 5b | real-time | Hotspot on tool call: "Before writing a single line — Kiro checks memory. The Skill kicked in." |
| 3 | Retrieved facts visible — **refund policy** (partial cap + 90-day window, sess-004) alongside payment patterns (cents, Stripe idempotency, JWT) | ✅ Cap 5c | real-time | Hotspot on refund policy result: "There it is. Partial cap, 90-day window — decided in session 4. Never written in code. Retrieved from memory." |
| 4 | Kiro writes correct code, first pass — policy baked in: cap at original minus prior refunds, 90-day window enforced (422 otherwise), per-attempt idempotency key. Citation visible: "Per the refund policy from session 4…" | ✅ Cap 5d | real-time | Hotspot on citations: "It cites its sources. Not training data — your team's sessions." Hotspot on cap + window: "Capped. Windowed. The policy Act 1 never knew about." |

### Side-by-side contrast

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 5 | **Side-by-side** — Act 1 (over-refunds, no window, amount-keyed idempotency) on Screen 1 next to Act 2 (capped, windowed, cites session 4) on Screen 2. Same prompt. | ✅ Cap 5e | real-time | Hotspot spanning both screens: "Left: over-refunds, no time limit, amount-based key. Right: capped, windowed, cites the decision. Same prompt. Same Kiro. Different memory." |

### Write beat — turn Act 1's bug into team memory

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 6 | (If Kiro applied retry/backoff unprompted) Call it out: "Notice it applied the retry-with-backoff from our charge path to the refund call — I never asked." | ✅ Cap 5f | real-time | Hotspot: "Pattern-matched our own conventions. Never asked. Memory carries the reasoning, not just the decisions." |
| 7 | Jeff types: `One more thing — the refund idempotency key can't be amount-based; two equal partial refunds would collide. Use a per-attempt UUID (refund-{uuid}). Save that as a decision so we never repeat it.` | ✅ Cap 5g | compress | Hotspot on prompt: "Act 1 shipped that bug. Now we're turning the fix into team memory." |
| 8 | `save-knowledge-fact` tool call fires — inputs expanded: fact text (per-attempt UUID rule), category, project, importance | ✅ Cap 5h | real-time | Hotspot on tool call: "save-knowledge-fact — Kiro calls Agent Builder, Agent Builder triggers an Elastic Workflow, Workflow writes to Elasticsearch." |
| 9 | Kiro confirms save | ✅ Cap 5i | compress | Hotspot on confirmation: "That bug the amnesiac version shipped? Fixed — and now in team memory. Next session, nobody repeats it." |

---

## Scene 6 — Act 3: Cross-session read-back · ~2 min

**Purpose:** New session, teammate framing — the idempotency-key rule saved in Act 2 is immediately retrievable. Proves the write→read loop.
**State:** Post-Act-2 (per-attempt-UUID idempotency rule saved). Fresh Kiro session — do NOT reuse Act 2 session. checkout-memory agent.

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 1 | New Kiro session, then `/agent` → **checkout-memory** (fresh session = re-select the agent, or the memory tools won't fire). Frame it: "Now I'm a teammate. Brand new context, about to add another Stripe write." Type: `What's our convention for idempotency keys on refunds?` | ✅ Cap 6a | compress | Hotspot on prompt: "Brand new session. A bug fixed minutes ago by a different developer." |
| 2 | `search-knowledge-facts` fires → returns the per-attempt-UUID rule saved in Act 2 | ✅ Cap 6b | real-time | Hotspot on tool call: "Same tool. Different session. Different developer. Same memory." |
| 3 | Response: per-attempt UUID (`refund-{uuid}`), never amount-based — exact rule from Act 2's write beat | ✅ Cap 6c | real-time | Hotspot on answer: "Retrieved instantly. A bug fixed in Act 2 is now team memory. Cross-session, cross-machine, cross-team." |

---

## Scene 7 — Kibana: audit trail · ~2 min

**Purpose:** Show governance and observability — nothing is a black box.
**App:** Browser → Kibana Agent Builder

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 1 | Agent Builder home — `checkout-service-memory` agent in list | ✅ Cap 7a | compress | Hotspot on agent row: "One agent. Lives in Kibana. Any client — Kiro, a web app, another agent — can call it via MCP." |
| 2 | Click into agent — system instructions visible, tools listed (4 read + save-knowledge-fact write) | ✅ Cap 7b | compress | Hotspot on tool list: "Five tools — four for reading, one for writing. Same agent. Same MCP endpoint." |
| 3 | Click into `save-knowledge-fact` tool — type: workflow, workflow_id visible | ✅ Cap 7c | real-time | Hotspot on type field: "Workflow tool. Kiro calls Agent Builder → Agent Builder triggers an Elastic Workflow → Workflow writes to Elasticsearch. Fully orchestrated, no custom server." |
| 4 | Navigate to **Conversations** tab — the Act 2 session visible, tool calls expanded (query sent, documents returned) | ✅ Cap 7d | real-time | Hotspot on expanded tool call: "Every agent call, every tool, every document retrieved — logged. Not a black box. Governance and audit trail for free." |

---

## Scene 8 — Close / CTA (static slide)

**Captures:** 1

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 1 | Closing slide with repo URL + blog URL | ✅ Cap 8a | — | Hotspot on repo URL: "Clone it. Five-minute setup. Your agents have persistent memory." Hotspot on stack summary: "Bedrock handles inference. Elastic handles memory. Two services, composable." |

---

## Re-take Cheat Sheet

See run-book **Reset procedures between takes** for exact commands. Summary:

| Scene | Reset | Note |
|-------|-------|------|
| 2 — Act 1 | `git -C ~/repos/checkout-service-demo checkout .`; fresh stock Kiro session | Verify policy gaps (no cap, no window, amount-based key) against `demo_scripts/reference/refunds-amnesiac.py` |
| 3 — Live-build | `python3 setup/demo-setup.py --clean` | Empty Elastic — scripts must show *creation*, not "already exists" |
| 4 — Wire memory | `python3 setup/demo-setup.py --prep`, restart Kiro | Removes elastic-memory from mcp.json |
| 5 — Act 2 | `git checkout .` in codebase; `--reset` if stray fact saved; fresh session | Must be baseline — refunds must not already exist from Act 1 |
| 6 — Act 3 read-back | Fresh Kiro session | Do NOT reuse the Act 2 session. Per-attempt-UUID rule must be saved from Act 2. |
| 7 — Kibana | None | Re-navigate from Agent Builder home — read-only |
| Full retake | `python3 setup/demo-setup.py --reset` + `git checkout .` in codebase | Restores 67 docs, agent re-created |

**Write path — RESOLVED (2026-06-11):** the `save-knowledge-fact` write beat works end-to-end (agent → tool → workflow → ES), verified via the converse API. The 9.5 fix was nesting workflow `inputs` under the manual trigger so Agent Builder exposes the tool params. **Only gotcha before recording:** restart Kiro so it reloads the re-derived tool, then confirm Scene 5's save fires and `knowledge-facts` goes 18 → 19. See run-book "Write path — RESOLVED".

---

## Narration Style

Keep hotspot text **punchy** — one observation per hotspot, max 2 sentences.

**Don't say:** "As you can see, the agent is now calling the search-knowledge-facts tool which is performing a semantic search using Jina v5 embeddings against the knowledge-facts index in Elasticsearch..."

**Do say:** "Tool call. Jina encodes the question. Elasticsearch finds the closest facts."

Cadence: **show** → **name what's happening** → **say why it matters**.
