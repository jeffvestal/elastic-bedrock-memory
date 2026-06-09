---
type: final
title: "AWS Summit NYC 2026 — Navattic Shot Sheet"
status: pre-recording
category: content
priority: high
created: 2026-06-02
updated: 2026-06-09
tags: [aws-summit-2026, navattic, demo, elastic-bedrock-memory, shot-sheet]
---

# AWS Summit NYC 2026 — Navattic Shot Sheet

**Recording target:** Click-through demo for "From Stateless to Stateful" session
**Source script:** `demo_scripts/aws-summit-2026-practice-guide.md`
**Repo:** `github.com/jeffvestal/elastic-bedrock-memory`
**Total shots:** ~23 steps across 7 scenes
**Demo runtime:** ~10 minutes in Navattic

### Kibana (Agent Builder):
https://bedrock-memory-demo-e86908.kb.us-east-1.aws.elastic.cloud

### Kiro:
Kiro running with checkout-service project, `~/.kiro/settings/mcp.json` wired to Agent Builder,
`~/.kiro/agents/checkout-memory.json` installed (the Kiro Skill)

---

## Pre-Recording Setup

### Step 1 — Data and infra (run from `elastic-bedrock-memory/`)
```bash
# First-time only: create workflow + agent (write path setup)
python3 setup/demo-setup.py --setup

# Re-seed within 2 weeks of recording so timestamps look recent
python3 setup/demo-setup.py --reset

# Verify everything is green — should show 5/5 tools (read + write)
python3 setup/demo-setup.py
```

### Step 2 — Kiro Skill
```bash
cp kiro-config/checkout-memory-agent.json ~/.kiro/agents/checkout-memory.json
```

### Step 3 — Prep for recording (Scenes 2–3)
```bash
# Removes elastic-memory from mcp.json + resets checkout-service-demo README
python3 setup/demo-setup.py --prep
```
Then restart Kiro. Scenes 2 and 3 run with NO memory tools.

### Step 4 — Between Scene 3 and Scene 4
```bash
# Restores elastic-memory to mcp.json
python3 setup/demo-setup.py --add-mcp
```
Then restart Kiro. Scene 4 shows adding the config; Scenes 5+ have full memory.

### Step 5 — Scene-specific checks
- [ ] **Scenes 2–3:** launch Kiro from `~/repos/checkout-service-demo/` — NOT from elastic-bedrock-memory (seed.py would give away answers)
- [ ] Confirm "What stack are we using?" gets a blank response from checkout-service-demo before recording Scene 3
- [ ] **Scene 4+:** launch Kiro from any directory with elastic-memory active
- [ ] Test Scene 5 question sequence end-to-end: Q1 (DB) → Q2 (recent work) → Q3 (auth) → Q4 (save CDN) → Q4b (new session reads CDN) — verify each fires correct tool
- [ ] Before Q4: confirm `save-knowledge-fact` tool shows in Kiro's `/mcp list` output
- [ ] After Q4 save: verify doc count in `knowledge-facts` increased by 1 (`python3 setup/demo-setup.py` will show this)
- [ ] **Scene 6:** before recording, open Kibana chat with checkout-service-memory agent and ask "What payment processor did we choose, and why?" — verify tool call fires and response is correct; this also populates the Conversations tab

### Visual setup (all scenes)
- [ ] Browser open to Kibana Agent Builder — `checkout-service-memory` agent visible
- [ ] Font 16px+ in both Kiro and Kibana
- [ ] Window 1920×1080, menubar/dock hidden

---

## Navattic Notes

- Each row below = one Navattic step.
- **Highlight / Hotspot** column = tooltip text, copy-paste ready.
- For tool call steps: capture two screenshots (before response + after complete). Wire as sequential auto-advance.
- Keep hotspots to 1–2 sentences. Show → name it → say why it matters.

---

## Scene 1 — Architecture (static slide)

**App:** Slide deck | **Captures:** 1

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 1 | Architecture diagram showing two paths from Kiro: (1) Kiro → Amazon Bedrock for inference, (2) Kiro → Elastic Agent Builder → Elasticsearch for memory | ✅ Cap 1a | Annotate both arrows. **Bedrock arrow:** "Amazon Bedrock — this is where inference runs. Your AWS account, your model." **Agent Builder arrow:** "Elastic Agent Builder — this is where memory lives. Agent Builder exposes a native MCP endpoint. No custom server to build or operate." |

---

## Scene 2 — Within-session memory (Kiro, same session)

**Purpose:** Show what Kiro already does — working memory within a session. Sets up the contrast.
**App:** Kiro launched from `~/repos/checkout-service-demo/` — a minimal project with no decision history in the files. This is the "developer in their actual codebase" scenario. Without elastic-memory in mcp.json. | **Captures:** 2

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 1 | Kiro chat — developer types: `I'm building a checkout service. We're using FastAPI and Aurora PostgreSQL.` — message sent | ✅ Cap 2a | Hotspot on message: "Developer drops some context into the session." |
| 2 | Developer asks: `What stack are we using?` → Kiro responds correctly: FastAPI, Aurora PostgreSQL | ✅ Cap 2b | Hotspot on response: "Kiro remembers — within this session. Working memory. Now watch what happens when you start a new session." |

---

## Scene 3 — Stateless failure (Kiro, no memory tools)

**Purpose:** Show cross-session amnesia — the problem this demo solves.
**State:** elastic-memory still NOT in mcp.json. Still running from `~/repos/checkout-service-demo/`. Fresh Kiro session — no prior context. Kiro can grep the project but there's nothing there to find.

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 1 | Kiro chat (stock agent, no memory tools) — question typed: `What stack are we using for the checkout service?` | ✅ Cap 3a | Hotspot on question: "Same question. Different session. No context set." |
| 2 | Kiro response — no memory: doesn't know the stack, no access to previous sessions | ✅ Cap 3b | Hotspot on response: "Session ended. Context gone. Kiro has no idea — and it can't. This is stateless by default." |

---

## Scene 4 — Wire the memory (script + Kiro Skill + agent select)

**Purpose:** Show the full wiring: run the setup script to add the MCP config, show the Kiro Skill, select the agent.
**State:** mcp.json does NOT have elastic-memory yet (--prep was run before Scene 2). This scene adds it.
**App:** Terminal / editor / Kiro | **Captures:** 5

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 1 | `~/.kiro/settings/mcp.json` open — elastic-memory block absent (mcpServers empty or missing the entry) | ✅ Cap 4a | Hotspot: "mcp.json — Kiro's list of MCP servers. No elastic-memory yet." |
| 2 | Terminal — run `python3 setup/demo-setup.py --add-mcp` — output shows "Added 'elastic-memory' to mcp.json" | ✅ Cap 4b | Hotspot on command: "One script. Adds the Elastic Agent Builder MCP endpoint to Kiro." |
| 3 | `~/.kiro/settings/mcp.json` open again — elastic-memory block now present: url pointing to `/api/agent_builder/mcp`, three headers | ✅ Cap 4c | Hotspot on `"url"` line: "Agent Builder's native MCP endpoint — no custom server to build or operate." Hotspot on headers: "Three headers. That's the entire integration." |
| 4 | `~/.kiro/agents/checkout-memory.json` open — prompt visible, tools list showing `@elastic-memory/*` entries, `"model": null` | ✅ Cap 4d | Hotspot on prompt: "A Kiro agent Skill — tells Kiro: before answering project questions, check memory first." Hotspot on tools: "Each `@elastic-memory/` entry is a tool backed by Elasticsearch." Hotspot on `"model": null`: "Auto mode — Kiro runs on Amazon Bedrock. Inference and memory: separate, composable." |
| 5 | Kiro — restart, type `/agent` → picker shows checkout-memory (Global) with description "Checkout service dev assistant with Elastic long-term memory" → select it | ✅ Cap 4e | Hotspot on checkout-memory row: "The Kiro Skill — installed globally, available in any project. Select it and Kiro knows to check Elastic memory first." Hotspot on 'Global' label: "One install, any project directory." |

---

## Scene 5 — Kiro with memory (THE MAIN SCENE, ~6 min)

**App:** Kiro — checkout-memory agent, elastic-memory MCP connected
**Recording note:** All three questions in one session. Questions are designed so each is out-of-scope from the previous answer — each one fires a fresh tool call naturally. No session restarts needed.

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 0 | New Kiro session — type `/agent` → select checkout-memory | ✅ Cap 5a | Hotspot: "New session. Same agent. The Skill is always there — the memory is always there." |

### Question 1 — "What database are we using and why?" (~2 min)

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 1 | Kiro chat — question typed: `What database are we using for the checkout service, and why did we choose it?` | ✅ Cap 5b | Hotspot on question: "Same project, new session. The Skill kicks in." |
| 2 | Kiro — tool call firing: `search-knowledge-facts` with nlQuery visible | ✅ Cap 5c — auto-advance 2s | Hotspot on tool call: "Agent calling search-knowledge-facts. Jina encodes the question. Elasticsearch returns the semantically closest facts." |
| 3 | Full response — Aurora PostgreSQL: ACID transactions for payment integrity, relational JOINs for order history reporting, Aurora Serverless v2 for scale | ✅ Cap 5d | Hotspot on answer: "The decision. The rationale. From session 1, two weeks ago. It didn't hallucinate — it retrieved." |

### Question 2 — "What did we last work on?" (~2 min)
*Continuing same session — auth not mentioned yet, Q2 fires three tools in sequence.*

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 4 | Kiro chat — question: `Catch me up — what were we working on in the last session?` | ✅ Cap 5e | Hotspot on question: "Monday morning question. Or returning from a week off." |
| 5 | Three tool calls firing in sequence: `get-recent-conversations` → `list-sessions` → `search-knowledge-facts` (nlQuery: "most recent work session sess-010") | ✅ Cap 5f — auto-advance 2s | Hotspot: "Three tools. The agent builds context: get recent turns, list all sessions, then semantically retrieve the latest session's details. It's composing an answer, not guessing." |
| 6 | Full response — sess-010: structured JSON logs to CloudWatch, X-Ray distributed tracing via aws_xray_sdk, correlation IDs via X-Request-ID propagated through Python contextvars, custom metrics (cart_conversion_rate, checkout_failures_total, payment_latency_p99) | ✅ Cap 5g | Hotspot on session content: "Last session: observability. CloudWatch, X-Ray, correlation IDs, custom metrics — the full AWS-native monitoring stack, recalled from memory." |

### Question 3 — "Auth approach?" (~2 min)
*Continuing same session — auth hasn't appeared in Q1 (DB-focused) or Q2 (observability), so the agent retrieves it fresh.*

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 7 | Kiro chat — question: `What auth approach did we decide on — JWT or opaque tokens?` | ✅ Cap 5h | Hotspot on question: "The kind of question a new team member asks on day one." |
| 8 | Tool call: `search-knowledge-facts` — different nlQuery | ✅ Cap 5i — auto-advance 2s | (no hotspot — let the retrieval speak) |
| 9 | Full response — JWT (15 min expiry) with refresh tokens; opaque tokens rejected because validation at the gateway removes the per-request round-trip to an auth server; Okta OIDC for SSO, OAuth2 PKCE for mobile | ✅ Cap 5j | Hotspot on JWT answer: "Correct — from session data, not training data." Hotspot on opaque tokens: "It knows what was considered and rejected, and why. The reasoning is part of the memory." |

### Question 4 — "Save a decision" (~1 min)
*Write beat — demonstrates memory isn't pre-seeded. This decision doesn't exist yet in the index.*

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 10 | Kiro chat — question: `We've decided to use Cloudflare CDN with a 5-minute TTL for static assets. Save this to memory.` | ✅ Cap 5k | Hotspot on question: "Now let's prove memory isn't pre-seeded magic. We're writing a new decision." |
| 11 | Tool call: `save-knowledge-fact` firing — inputs visible: fact, category, project, importance | ✅ Cap 5l — auto-advance 2s | Hotspot on tool call: "save-knowledge-fact — a workflow tool. Kiro calls Agent Builder, Agent Builder triggers an Elastic Workflow, Workflow writes a document to Elasticsearch." |
| 12 | Kiro response confirming save: "I've saved the Cloudflare CDN decision to memory." | ✅ Cap 5m | Hotspot on confirmation: "Saved. In Elasticsearch. Right now." |

### Question 4b — Read-back (new session) (~30 sec)
*Start a fresh Kiro session to prove cross-session persistence.*

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 13 | New Kiro session — `/agent` → checkout-memory — question: `What CDN are we using?` | ✅ Cap 5n | Hotspot on question: "New session. Brand new context. What does memory say?" |
| 14 | Tool call: `search-knowledge-facts` fires | ✅ Cap 5o — auto-advance 2s | (no hotspot — let the retrieval speak) |
| 15 | Response: Cloudflare CDN, 5-minute TTL — retrieved from the fact just written | ✅ Cap 5p | Hotspot on response: "Cloudflare. Exactly what we just told it. Memory isn't pre-seeded — it's whatever you tell it." |

---

## Scene 6 — Kibana: under the hood (~2 min)

**App:** Browser → Kibana Agent Builder | **Purpose:** Show the agent itself — config, Skill, then call it directly via Kibana chat so the instructions and Skill actually activate. Kiro calls tools directly via MCP; the Converse API is for direct agent clients (Kibana chat, other integrations). This scene shows both sides.

**Pre-recording:** Ask the agent a question in Kibana chat BEFORE recording Scene 6, so a conversation already exists in the Conversations tab.

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 1 | Agent Builder home — `checkout-service-memory` agent in list | ✅ Cap 6a | Hotspot on agent row: "One agent. Lives in Kibana. No separate deployment. Any client — Kiro, a web app, another agent — can call it." |
| 2 | Click into agent — system instructions visible, **5 tools** listed (4 read + save-knowledge-fact) | ✅ Cap 6b | Hotspot on instructions: "System prompt: always use memory tools before answering." Hotspot on tool list: "5 tools — 4 for reading, 1 for writing. Same agent. Same MCP endpoint." |
| 3 | Click into `save-knowledge-fact` tool — type: workflow, workflow_id visible | ✅ Cap 6c | Hotspot on type: "workflow — this tool triggers an Elastic Workflow. The workflow writes a document to Elasticsearch. Agent Builder orchestrates the whole path." |
| 4 | Navigate to **Skills** tab — `checkout-memory-retrieval` Skill visible with description | ✅ Cap 6d | Hotspot on Skill: "Agent Builder Skill — a runbook. Kiro's Skill defines *when* to use memory. This Skill defines *how*. The agent follows this when called directly." |
| 5 | Open Kibana chat with `checkout-service-memory` agent — ask: `What CDN are we using for static assets?` — `search-knowledge-facts` fires, returns Cloudflare | ✅ Cap 6e | Hotspot on tool call: "Agent Builder chat reading what Kiro just wrote. Same memory store. Different client." Hotspot on response: "Cloudflare — retrieved from the fact Kiro saved in Scene 5." |
| 6 | Navigate to **Conversations** tab — the chat session just recorded is visible with tool calls expanded | ✅ Cap 6f | Hotspot on conversation: "Full audit trail — every agent call, every tool invoked, every document retrieved. Logged automatically." |

---

## Scene 7 — Close / CTA (static slide)

**Captures:** 1

| # | Action | Capture? | Highlight / Hotspot |
|---|--------|----------|---------------------|
| 1 | Closing slide with repo URL + blog URL | ✅ Cap 7a | Hotspot on repo URL: "Clone it. 5-minute setup. Your agents have persistent memory." Hotspot on stack summary: "Bedrock handles inference. Elastic handles memory. Two services, composable." |

---

## Re-take Cheat Sheet

| Scene | Reset | Note |
|-------|-------|------|
| 2 — Within-session | Clear Kiro chat, start fresh | Must be running from `~/repos/checkout-service-demo/` |
| 3 — Stateless | Fresh Kiro session | Same dir, same no-MCP state — Kiro has nothing to grep |
| 4 — Config | Run `--prep` again, restart Kiro | Re-run `--prep` to clear mcp.json; then re-record script + before/after captures |
| 5 — Memory questions | Start new session, `/agent` → checkout-memory | Ask Q1 (DB), Q2 (recent work), Q3 (auth), Q4 (save CDN) in sequence — order matters for Q1-Q3 (each must be out-of-scope from prior answer). Q4b needs a fresh session. |
| 5b — Read-back | Fresh Kiro session, `/agent` → checkout-memory | Start new session for Q4b (What CDN?) — do NOT ask in same session as Q4 save |
| 6 — Kibana | None | Re-navigate from Agent Builder home — read-only |
| Full retake | `python3 setup/demo-setup.py --reset` + clear Kiro chat | Restores all 67 docs; agent re-created |

---

## Narration Style

Keep hotspot text **punchy** — one observation per hotspot, max 2 sentences.

**Don't say:** "As you can see, the agent is now calling the search-knowledge-facts tool which is performing a semantic search using Jina embeddings against the knowledge-facts index in Elasticsearch..."

**Do say:** "Tool call. Jina encodes the question. Elasticsearch finds the closest facts."

Cadence: **show** → **name what's happening** → **say why it matters**.
