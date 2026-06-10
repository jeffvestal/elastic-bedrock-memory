---
type: final
title: "AWS Summit NYC 2026 — Navattic Shot Sheet"
status: pre-recording
category: content
priority: high
created: 2026-06-02
updated: 2026-06-10
tags: [aws-summit-2026, navattic, demo, elastic-bedrock-memory, shot-sheet]
---

# AWS Summit NYC 2026 — Navattic Shot Sheet

**Recording target:** Click-through demo for "From Stateless to Stateful" session
**Source of truth:** `demo_scripts/aws-summit-2026-demo-runbook.md` (run-book wins on all conflicts)
**Repo:** `github.com/jeffvestal/elastic-bedrock-memory`
**Total shots:** ~35 steps across 8 scenes
**Demo runtime:** ~12 minutes in Navattic

**Narrative spine:** One task — *add a refund endpoint* — built **wrong** without memory (Act 1), the memory system **built live** in front of the audience, **wired** to Kiro, then the same task built **right** with memory (Act 2). Cross-session read-back and Kibana audit trail close it out.

### Kibana (Agent Builder):
https://bedrock-memory-demo-e86908.kb.us-east-1.aws.elastic.cloud

### Kiro:
Kiro launched from `~/repos/checkout-service-demo`. For Act 1 (Scene 2): stock agent, no elastic-memory in mcp.json. For Act 2 (Scene 5): checkout-memory agent active, elastic-memory wired.

---

## Pre-Recording Setup

Follow the state matrix in the run-book exactly. Abbreviated here for reference:

```bash
cd ~/repos/elastic-bedrock-memory

# One-time baseline — clean project, re-seeds on next Segment 3 capture
python3 setup/demo-setup.py --nuclear

# Reset codebase to baseline before Act 1 AND Act 2 captures
git -C ~/repos/checkout-service-demo checkout .
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

## Scene 2 — Act 1: Amnesia (refunds, built wrong) · ~6 min

**Purpose:** Show what an amnesiac Kiro builds when it has no access to the team's decision history.
**State:** Stock Kiro agent. `elastic-memory` NOT in mcp.json. Codebase at baseline (`git checkout .`). Launched from `~/repos/checkout-service-demo/`.
**Note:** See run-book "Target slips" and "Eliciting the slips" for live elicitation guidance. Need ~3 of 4 slips to land the point. Verify take against `demo_scripts/reference/refunds-amnesiac.py`.

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 1 | (Optional) Kiro chat — type: `I'm back on the checkout service. We're adding refunds today.` Kiro acknowledges. | ✅ Cap 2a | compress | Hotspot: "Kiro remembers what you tell it in this session. Working memory — fine. Watch what it doesn't have." |
| 2 | The ask (verbatim): `I need to add refunds to the checkout service. Add a POST endpoint that lets a customer request a refund on an order — support partial refunds where they can pass a dollar amount to refund. Wire it up to Stripe.` | ✅ Cap 2b | compress | Hotspot on prompt: "Same prompt used in Act 2 — word for word. Only one thing changes." |
| 3 | Kiro streams wrong code — float dollar input and/or float math in refund amount | ✅ Cap 2c | compress | Hotspot on float variable: "Float. Our team already paid for this exact mistake with a production 1-cent rounding bug." |
| 4 | Jeff types correction 1: `Hold on — we store money as integer cents, never floats. We had a 1-cent rounding bug from exactly this kind of math two weeks ago. Use the money helpers.` Kiro fixes. | ✅ Cap 2d | real-time | Hotspot on correction: "Correction 1. Kiro fixes it — because you remembered." |
| 5 | Jeff types correction 2: `That Stripe refund needs an idempotency key like our charge path does, or a retry double-refunds the customer.` Kiro fixes. | ✅ Cap 2e | real-time | Hotspot on correction: "Correction 2. The idempotency pattern. Already in our history — not in Kiro's context." |
| 6 | Jeff types correction 3: `This route isn't authenticated — every other route uses get_current_user.` Kiro fixes. | ✅ Cap 2f | real-time | Hotspot on correction: "Correction 3. JWT on every route. Our convention. Kiro had to be told." |
| 7 | (If applicable) Jeff types correction 4: `And guard against double refunds and refunding more than the order total.` Kiro fixes. | ✅ Cap 2g | real-time | Hotspot on correction: "Correction 4. The idempotency ledger. Another thing the team already decided." |
| 8 | Hold on final hand-corrected diff — all four slips visible as corrections | ✅ Cap 2h | real-time | Hotspot on diff: "Everything fixed — by you. Because you remembered what Kiro couldn't." |
| 9 | Breaking point (Jeff to the room): "Every one of those corrections is something my team already decided. The cents rule — we paid for that with a production bug. The idempotency pattern, the auth convention. It's written down in past sessions, it's in my head, it's in a teammate's brain. Kiro had none of it. And tomorrow, new session, I do this all over again. That's the amnesia tax — every session, every teammate, forever." | ✅ Cap 2i | real-time | No hotspot — let it land. |

---

## Scene 3 — Live-build the memory system · ~10 min

**Purpose:** Build the complete memory system on camera. Audience sees it isn't magic — it's three scripts.
**State:** Freshly reset Elastic project (`--nuclear` run before this take). Terminal + browser (Kibana). Launched from `~/repos/elastic-bedrock-memory/`.

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

**Purpose:** Same prompt, memory-wired Kiro, correct output first pass with citations. Side-by-side contrast. Write beat.
**State:** checkout-memory agent active, elastic-memory wired, fresh Kiro session, codebase **reset to baseline** (`git checkout .`). Launched from `~/repos/checkout-service-demo/`.

### The ask (VERBATIM SAME as Act 1)

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 1 | Kiro chat — type the IDENTICAL prompt: `I need to add refunds to the checkout service. Add a POST endpoint that lets a customer request a refund on an order — support partial refunds where they can pass a dollar amount to refund. Wire it up to Stripe.` | ✅ Cap 5a | compress | Hotspot on prompt: "Same prompt. Word for word. The only thing that changed is memory." |
| 2 | **MONEY SHOT** — `search-knowledge-facts` tool call fires BEFORE any code is written. nlQuery visible (something like: "money handling, payments, Stripe, refund decisions"). | ✅ Cap 5b | real-time | Hotspot on tool call: "Before writing a single line — Kiro checks memory. The Skill kicked in." |
| 3 | Retrieved facts visible — integer cents (sess-005), Stripe idempotency (sess-004), retry/backoff (sess-007), JWT auth (sess-002) | ✅ Cap 5c | real-time | Hotspot on results: "Four decisions retrieved. The house rules — from the sessions that established them." |
| 4 | Kiro writes correct code, first pass — integer cents, idempotency key, `get_current_user` dependency, double-refund guard. Citations visible: "Based on the decision in session 5… matching the idempotency pattern from session 4…" | ✅ Cap 5d | real-time | Hotspot on citations: "It cites its sources. Not training data — your team's sessions." Hotspot on correct code: "No float. Idempotency key. Auth. Guard. Correct, first pass." |

### Side-by-side contrast

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 5 | **Side-by-side** — Act 1's hand-corrected mess (Screen 1) next to Act 2's correct-first-pass output (Screen 2). Same prompt. | ✅ Cap 5e | real-time | Hotspot spanning both screens: "Left: four corrections, one by one. Right: correct, unprompted. Same prompt. Same Kiro. Different memory." |

### Go deeper — backoff and new policy

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 6 | (If Kiro applied retry/backoff unprompted) Call it out: "Notice it applied the retry-with-backoff from our charge path to the refund call — I never asked." | ✅ Cap 5f | real-time | Hotspot: "Pattern-matched our own conventions. Never asked. Memory carries the reasoning, not just the decisions." |
| 7 | Jeff types: `Now enforce the refund rules: partial refunds up to the original charge minus any prior refunds, and only within 90 days of the order. Then save that policy to memory.` | ✅ Cap 5g | compress | Hotspot on prompt: "A new decision — doesn't exist anywhere yet. Not in code, not in memory." |
| 8 | `save-knowledge-fact` tool call fires — inputs expanded: fact text, category, project, importance | ✅ Cap 5h | real-time | Hotspot on tool call: "save-knowledge-fact — Kiro calls Agent Builder, Agent Builder triggers an Elastic Workflow, Workflow writes to Elasticsearch." |
| 9 | Kiro confirms save | ✅ Cap 5i | compress | Hotspot on confirmation: "That decision is now in Elasticsearch. Kiro just wrote to the team's memory." |

---

## Scene 6 — Act 3: Cross-session read-back · ~2 min

**Purpose:** New session, different developer framing — the saved fact is immediately retrievable.
**State:** Post-Act-2 (90-day/partial-cap fact saved). Fresh Kiro session — do NOT reuse Act 2 session. checkout-memory agent.

| # | Action | Capture? | Timing | Highlight / Hotspot |
|---|--------|----------|--------|---------------------|
| 1 | New Kiro session — frame it: "Now I'm a teammate. Brand new context." Type: `What's our refund policy — can customers get partial refunds, and is there a time limit?` | ✅ Cap 6a | compress | Hotspot on prompt: "Brand new session. A decision made minutes ago by a different developer." |
| 2 | `search-knowledge-facts` fires → returns 90-day / partial-cap fact saved in Act 2 | ✅ Cap 6b | real-time | Hotspot on tool call: "Same tool. Different session. Different developer. Same memory." |
| 3 | Response: 90-day window, partial refunds up to original charge minus prior refunds — exact policy from Act 2 | ✅ Cap 6c | real-time | Hotspot on answer: "Retrieved instantly. The memory isn't on your laptop. It's in Elasticsearch — cross-session, cross-machine, cross-team." |

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
| 2 — Act 1 | `git -C ~/repos/checkout-service-demo checkout .`; fresh stock Kiro session | Verify slips against `demo_scripts/reference/refunds-amnesiac.py` |
| 3 — Live-build | `python3 setup/demo-setup.py --nuclear` | Clean project — scripts must show *creation*, not "already exists" |
| 4 — Wire memory | `python3 setup/demo-setup.py --prep`, restart Kiro | Removes elastic-memory from mcp.json |
| 5 — Act 2 | `git checkout .` in codebase; `--reset` if stray fact saved; fresh session | Must be baseline — refunds must not already exist from Act 1 |
| 6 — Act 3 read-back | Fresh Kiro session | Do NOT reuse the Act 2 session |
| 7 — Kibana | None | Re-navigate from Agent Builder home — read-only |
| Full retake | `python3 setup/demo-setup.py --reset` + `git checkout .` in codebase | Restores 67 docs, agent re-created |

**Open risk (from run-book):** Verify `save-knowledge-fact` workflow fires and writes end-to-end before recording Scene 5's write beat. Fallback procedures in run-book "Open risk" section.

---

## Narration Style

Keep hotspot text **punchy** — one observation per hotspot, max 2 sentences.

**Don't say:** "As you can see, the agent is now calling the search-knowledge-facts tool which is performing a semantic search using Jina v5 embeddings against the knowledge-facts index in Elasticsearch..."

**Do say:** "Tool call. Jina encodes the question. Elasticsearch finds the closest facts."

Cadence: **show** → **name what's happening** → **say why it matters**.
