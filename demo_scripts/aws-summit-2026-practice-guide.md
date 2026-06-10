---
type: final
title: "AWS Summit NYC 2026 — Practice Guide"
status: active
category: content
priority: high
created: 2026-06-02
updated: 2026-06-10
tags: [aws-summit-2026, practice, talk, elastic-bedrock-memory]
---

# AWS Summit NYC 2026 — Practice Guide

**Talk:** From Stateless to Stateful: Architecting Agent Memory with Elastic and Bedrock
**Duration:** 60 minutes, solo
**Audience:** AWS Summit builders — developers and architects
**Format:** Slides + live screen (~30 min of hands-on)

> **Note:** Slide numbers are finalized after the deck update. References below use segment names, not hard slide numbers.

---

## The Talk in One Paragraph

AI agents have amnesia. Every session starts at zero — no memory of what decisions were made, what failed, what the team already figured out. Stuffing everything into the context window is the brute-force workaround. It's expensive, slow, and still has a ceiling. The right fix is persistent, semantic, external memory — and Elasticsearch is already the right store for it. In this session you'll see how to wire Amazon Bedrock (via Kiro) to Elastic Agent Builder's native MCP endpoint, giving your agents cross-session recall of architectural decisions, past bugs, and institutional knowledge — at any scale, with no custom middleware.

---

## What's Unique / Why This Is Different

**Not a chatbot on docs.** The agent recalls actual decisions your team made — stored in Elasticsearch, retrieved with Jina semantic search. It returns the right answer even when the exact words don't match.

**No custom MCP server to build or operate.** Elastic Agent Builder exposes a native MCP endpoint. Point your IDE at it. Done.

**Jina semantic embeddings, zero pipeline.** One field type — `semantic_text` — auto-vectorizes at ingest. No embedding pipeline to build, maintain, or monitor.

**Kiro Skills wire the instinct.** A Kiro agent config (the Skill) tells Kiro when to consult memory. The MCP config provides the tools; the Skill provides the behavior. Both ship in the repo.

**Cross-session, cross-machine, cross-team.** The memory store is Elasticsearch. Any agent, any machine, any team member — same memory.

**Observable and auditable.** Every agent call is logged in Kibana Conversations. Every tool call shows what was queried and what was returned. Not a black box.

---

## Why the Audience Should Care

They're developers at AWS Summit. They're building with Bedrock, Kiro, or both. They've seen demos where AI summarizes docs or generates boilerplate. This shows something different: an agent that *remembers what your team decided* and *explains the rationale* — not from training data, from your data.

The practical unlocks:
- **Onboarding:** a new team member can ask the agent "what auth approach did we decide on?" and get the right answer with the reason.
- **Context recovery:** returning from a week off, ask "what did we work on last session?" and pick up exactly where you left off.
- **Institutional memory:** senior engineer leaves. The decisions stay.

**The line to land:** *"Your agents remember what you tell them. They don't remember what you decided last week. This is how you fix that."*

---

## Talk Structure and Timing

| # | Segment | Medium | Min |
|---|---------|--------|-----|
| 1 | Intro + amnesia hook | slides | 5 |
| 2 | Act 1 — amnesia in Kiro (refunds built wrong) | live screen | 6 |
| 3 | Live-build the memory system (indices → agent → tools → load history) | live screen | 10 |
| 4 | Wire memory to Kiro (mcp.json + Skill + /agent) | live screen | 3 |
| 5 | Act 2 — memory in Kiro (refunds nailed, go deeper, write beat) | live screen | 7 |
| 6 | Act 3 — teammate read-back + Kibana audit trail | live screen | 4 |
| 7 | Recap / design decisions | slides | 4 |
| 8 | FAQ-as-content | slides | 6 |
| 9 | Build-it-yourself / CTA | slides | 3 |
| 10 | Q&A | — | 5–8 |

Total content 1–9 ≈ 48 min; + Q&A ≈ 53–56. Slide time is ~18 min; live/screen content is ~30 min.

---

## Section-by-Section Practice Script

### Segment 1: Intro (5 min)

**Saying:**
> "Sixty minutes from now, you're going to have the full architecture — the code, the pattern, the repo — to give your AI agents persistent memory. Not longer context windows. Actual memory. Let's get into it."

> *(agenda slide)*
> "Nine sections. We'll spend most of our time live on screen. Questions at the end — but if something's unclear, flag me in the aisle."

The intro slides set up the stakes. Keep it tight — under 2 minutes on the pure agenda framing. The amnesia argument is coming: a few sentences here, then get to Kiro fast.

**They should think:** *This is going somewhere concrete.*

---

### Segment 1 (continued): The Amnesia Hook

This is a compressed setup, not the full pitch deck version. You're priming the audience for what they're about to *feel* in Act 1 — not pre-chewing the pain for them.

**Saying:**
> "By default, every AI agent you build is stateless. Session ends, memory goes with it. The workaround everyone reaches for: bigger context window. Stuff everything in. It's expensive, it's slow, and when the session ends it's gone anyway."

> "I want to show you the cost of that — not as a slide, but in code, right now."

**Pace this slowly.** Don't rush to the solution. Let the problem land for 30–45 seconds before you go to the screen. Then cut to Kiro.

**They should think:** *I've hit this wall. Let's see it break.*

---

### Segment 2: Act 1 — Amnesia in Kiro (6 min)

**Before you type anything:**

> "Here's the scenario. I'm a developer who's been building a checkout service for two weeks — ten sessions. We've made real decisions along the way: how we handle money, how we auth routes, how we wire Stripe. Kiro knows the codebase — it can read every file. What it doesn't have is any access to those decisions. Watch."

You're in `~/repos/checkout-service-demo`, stock Kiro, no elastic-memory in mcp.json.

*(Optional 20-second beat: type "I'm back on the checkout service. We're adding refunds today." Kiro acknowledges. "Kiro remembers what I tell it in this session — that's working memory, and it's fine. Watch what it doesn't have." Cut this if you're running long.)*

**The ask — type this verbatim:**
> "I need to add refunds to the checkout service. Add a POST endpoint that lets a customer request a refund on an order — support partial refunds where they can pass a dollar amount to refund. Wire it up to Stripe."

Watch Kiro build. Target three slips: float dollar amounts (reintroduces the 1-cent bug), no idempotency key on the Stripe refund call, no `get_current_user` on the new route. You need about three of four to make the point. See the run-book for eliciting tactics if Kiro behaves too well.

**Catch each slip as Jeff, not as narrator.** These are your corrections, in character:

> "Hold on — we store money as integer cents, never floats. We had a 1-cent rounding bug from exactly this kind of math two weeks ago. Use the money helpers."

> "That Stripe refund needs an idempotency key like our charge path does, or a retry double-refunds the customer."

> "This route isn't authenticated — every other route uses get_current_user."

Kiro fixes each one. **But only because you remembered.**

**Breaking point (to the room — take 45–60 seconds, let it land):**
> "Every one of those corrections is something my team *already decided*. The cents rule — we paid for that with a production bug. The idempotency pattern. The auth convention. It's in past sessions, it's in my head, it's in a teammate's brain. Kiro had none of it. And tomorrow, new session, I do this all over again. That's the amnesia tax — every session, every teammate, forever."

**They should think:** *I recognize this. I've done this. I've been the person who remembered so the AI didn't have to.*

---

### Segment 3: Live-Build the Memory System (10 min)

**Framing line (to the room):**
> "Kiro's amnesia isn't Kiro's fault — it has no memory store. So let me build one. Live. In under ten minutes."

You're in terminal + browser (Kibana). This is three commands.

**Command 1 — indices:**
```bash
python3 setup/create-indices.py
```
> "Three indices: conversation history, knowledge facts, session metadata. Look at this one field — `semantic_text`. That *is* the embedding pipeline. Jina v5 vectorizes every document at ingest. No pipeline to build, no model to host."

Show the mapping. Point at the `semantic_text` field. Don't linger — this is a teaching beat, not a lecture.

**Command 2 — agent and tools:**
```bash
python3 setup/create-agent.py
```
> "This creates the agent and its tools through Agent Builder's API — semantic search tools for fuzzy recall, ES|QL tools for structured recall, and a write tool. No custom server. Agent Builder *is* the MCP server."

**Command 3 — load history:**
```bash
python3 demo-data/seed.py
```
> "In a real workflow, every session writes here automatically. To save us two weeks, I've got ten realistic sessions — decisions, bug fixes, the whole arc — loading now. Sixty-seven documents."

Show the doc counts.

**Kibana glance:** Agent Builder → the `checkout-service-memory` agent now exists with its tools. Point at `semantic_text` in Index Management.

> "Built. A complete memory system — indices, embeddings, an agent, tools — in the time it took to say it."

**This segment is your buffer.** If pacing runs hot, cut the Kibana glance. If cold, expand the mapping explanation. Either way, land the finish line above before moving on.

**They should think:** *This took longer to describe than to build.*

---

### Segment 4: Wire Memory to Kiro (3 min)

Show mcp.json before — no elastic-memory block. Then:

```bash
python3 setup/demo-setup.py --add-mcp
```

Show mcp.json after — the elastic-memory block with a URL pointing at `/api/agent_builder/mcp` and three headers.

Open `~/.kiro/agents/checkout-memory.json` — the Skill. Point at two things: the system prompt ("before answering project questions, check memory first") and the tools list (`@elastic-memory/*`).

Restart Kiro → `/agent` → select **checkout-memory (Global)**.

> "Two files. An MCP config — a URL and three headers, pointing at Agent Builder's native endpoint. And a Skill that tells Kiro: check memory before you answer. That's the entire integration. Nothing to build, nothing to deploy."

**They should think:** *Two config files. I could do this this afternoon.*

---

### Segment 5: Act 2 — Memory in Kiro (7 min)

Codebase reset to baseline. Fresh Kiro session. checkout-memory agent active.

**Framing line:**
> "Same prompt. Word for word."

**Type the exact same ask as Act 1:**
> "I need to add refunds to the checkout service. Add a POST endpoint that lets a customer request a refund on an order — support partial refunds where they can pass a dollar amount to refund. Wire it up to Stripe."

**Before Kiro writes a single line of code**, it calls `search-knowledge-facts`. Let the tool call breathe on screen. The nlQuery comes back with integer cents, Stripe idempotency, retry/backoff, JWT auth — from sessions 2, 4, 5, 7. **This is the money shot. Don't talk over it.**

Then Kiro writes the refund route. Correctly, first pass. With citations: *"Based on the decision in session 5, amounts are integer cents… matching the idempotency pattern from session 4…"*

**Side-by-side contrast (if you have two screens):** Act 1's hand-corrected mess vs. this. Same prompt. One fought you; one knew the house rules.

> "Same prompt. Word for word. The only thing that changed is that Kiro can see what we already decided — so it just *does it right*. And it tells me where each rule came from."

**Go deeper — the "go longer" beat:**

If Kiro pattern-matched the retry/backoff from the charge path to the refund call without being asked, **call it out explicitly:**
> "Notice it applied the retry-with-backoff from our charge path to the refund call — I never asked. It pattern-matched our own conventions."

Then introduce the new decision:
> "Now enforce the refund rules: partial refunds up to the original charge minus any prior refunds, and only within 90 days of the order. Then save that policy to memory."

Watch `save-knowledge-fact` fire. Show the tool call with inputs expanded — fact, category, project, importance.

> "That decision didn't exist anywhere a minute ago — not in the code, not in memory. Now it's in Elasticsearch. Kiro just wrote to the team's memory."

**They should think:** *Memory changed what the agent built, not just what it answered.*

---

### Segment 6: Act 3 — Cross-Session + Audit Trail (4 min)

**New Kiro session.** Frame it:
> "Now I'm a teammate. Different machine. Brand new context. Nothing carried over."

Ask:
> "What's our refund policy — can customers get partial refunds, and is there a time limit?"

`search-knowledge-facts` fires → returns the 90-day / partial-cap fact saved in Act 2.

> "Brand new session. A decision made minutes ago by a different developer — retrieved instantly. That's cross-session, cross-machine, cross-team. The memory isn't on my laptop. It's in Elasticsearch."

**Kibana — the audit trail:**
Agent Builder → Conversations tab → open the recorded session → expand the tool calls.

> "Every agent call, every tool, every document retrieved — logged. Not a black box. This is governance and audit, for free."

**They should think:** *This is observable. I can see exactly what the agent knew and when it knew it.*

---

### Segment 7: Recap / Design Decisions (4 min)

Don't re-narrate the demo. The audience just watched it.

**Saying:**
> "Here's what I want you to take away from that. Act 1 and Act 2 had identical prompts. The code Kiro wrote in Act 2 was correct, first pass. Memory didn't just answer a question — it changed the quality of the *work*. The agent reasoned from your team's actual decisions instead of general priors."

> "That's the real unlock: you're not just helping the agent recall facts. You're encoding your team's judgment into every code generation, every design decision, every 'what should we do next' question — automatically, from context that already exists in your session history."

**Design decisions (one level deeper than "here's what we used"):**

> "`semantic_text` with Jina: the field is the pipeline. You get embedding-quality recall without an embedding pipeline to operate. That matters in production because there's less to break."

> "Agent Builder as the MCP server: no proxy layer, no custom server, no middleware. The tools are defined once in Kibana and exposed to any MCP-compatible client. Add a new IDE, same tools — no re-deployment."

> "The three-index schema: keeping conversation turns, extracted facts, and session metadata separate means you can query each independently — prune conversation history on a retention schedule, search only high-importance knowledge facts, list sessions by project. Clean separation, clean queries."

> "Bedrock and Elastic are composable, not competing. Bedrock handles inference. Elastic handles memory, search, and observability. Swap the inference layer for any model you want — the memory store doesn't care."

**They should think:** *I understand the shape of the architecture well enough to adapt it.*

---

### Segment 8: FAQ-as-Content (~6 min)

The full scripts for each question live in `demo_scripts/aws-summit-2026-faq.md`. These run as slides. Expand or contract to fill remaining time after Act 3.

The six questions, in order:
1. "I don't use Kiro — does this work with my IDE or agent?"
2. "What does this cost?"
3. "Does this only work with Amazon Bedrock / AWS?"
4. "Does it scale?"
5. "Is it secure, auditable, and governed?"
6. "How does memory get written and maintained — does it grow forever, and what about stale or conflicting facts?"

Take the questions in order; skip or compress the last one if you're running tight. The first three (IDE portability, cost, vendor lock) tend to be the live audience's top concerns.

---

### Segment 9: Build It Yourself / CTA (3 min)

**Saying:**
> "Everything I just showed you is in the repo. `github.com/jeffvestal/elastic-bedrock-memory`. Three setup scripts: create-indices, create-agent, seed. Plus two Kiro config templates: the MCP server config and the agent Skill."

> "Companion blog has the full walkthrough with architecture diagrams and code deep-dive. Link on the closing slide."

> "Clone the repo. Configure your `.env` with ES URL, Kibana URL, API keys. Run the three setup scripts. Copy the two Kiro configs into `~/.kiro/`. Restart Kiro. Ask your agent about the project."

> "If you have an Elastic Cloud account — free trial at cloud.elastic.co if you don't — the whole setup is about five minutes."

**Closing line:**
> "Bedrock handles the inference. Elastic handles the memory, the search, and the observability. Wire them together and your agents remember what matters. Questions."

---

## One-Line Story Per Section (for plane review)

| Section | One line |
|---------|----------|
| Intro | Memory is the missing layer. Today you're getting it. |
| Amnesia hook | Stateless by default. Context windows are a workaround, not a solution. |
| Act 1 — amnesia in Kiro | Same refund prompt; Kiro reintroduced three bugs we already paid to fix. |
| Live-build | Three commands. Indices, agent, tools, history — in under ten minutes. |
| Wire memory | Two config files. Done. |
| Act 2 — memory in Kiro | Same prompt, memory wired — correct first pass, sources cited, new fact saved. |
| Act 3 — cross-session + audit | New session, new machine, retrieved the decision instantly. Kibana shows every call. |
| Recap | Memory changed what the agent built, not just what it answered. |
| FAQ-as-content | Six common objections, answered honestly. |
| Build It | Clone, configure, three scripts, restart Kiro. Five minutes. |

---

## What They Should Leave Thinking

**The problem you solved:** AI agents today are stateless. They know your codebase. They have no idea what your team decided in a meeting last Thursday, or why you chose Aurora PostgreSQL, or what that 2am incident was about. The context window workaround is expensive, ephemeral, and doesn't scale.

**What you showed:** A stock Kiro built a refund endpoint with three bugs your team already solved. A memory-wired Kiro — same prompt — built it correctly, first pass, and cited the session where each decision was made. Then a new decision was saved live, read back from a fresh session, and the full audit trail appeared in Kibana. That's the complete loop: read, write, and observe.

**Why Elastic:** Agent Builder handles tool grounding, MCP serving, conversation logging, and audit trails — in Kibana, which they may already have. The MCP endpoint is built in. No custom server to write, deploy, or operate. Jina v5 `semantic_text` means no embedding pipeline — one field type, auto-vectorized at ingest.

**The one thing to remember:** Memory didn't just let the agent answer questions. It changed the quality of the code it wrote. That's the jump — from stateless to stateful, from general priors to your team's actual judgment.

---

## Quick Delivery Notes

- **Pace Act 1 slowly.** Let each slip land before moving to the next correction. The audience should feel the friction — that's the setup for Act 2's contrast.
- **Don't talk over the `search-knowledge-facts` call in Act 2.** That tool call is the visual payoff. Let it breathe.
- **The side-by-side contrast is optional but powerful.** If you have a second screen, use it. Act 1's hand-corrected code vs. Act 2's first-pass-correct code is a physical proof that needs no narration.
- **Segment 3 (live-build) is your time buffer.** It runs 8–12 minutes depending on how much you explain. Compress the Kibana glance if running hot; expand the mapping explanation if cold.
- **During recap:** don't re-narrate what they just watched. Go one level deeper — memory changed the quality of the work, not just the answers. That's the framing that hasn't been said yet.
- **Questions tend toward:** "what if I have a different IDE?" (any MCP-compatible client works), "does this work with non-AWS inference?" (Agent Builder MCP endpoint doesn't care which model is calling it), "what does it cost?" (Elastic Cloud serverless + Bedrock free tier for demo — production pricing depends on usage). All six live in the FAQ file.
- **Don't go over time.** Cut from the Kibana audit segment or FAQ if running long — the build-it-yourself CTA is the one they'll act on.
