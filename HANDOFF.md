# Handoff: elastic-bedrock-memory Demo — AWS Summit NYC 2026

**Date:** 2026-06-09
**Talk:** From Stateless to Stateful: Architecting Agent Memory with Elastic and Bedrock
**Event:** AWS Summit NYC, June 17, 2026
**Repo:** github.com/jeffvestal/elastic-bedrock-memory (currently private — make public before June 17)

---

## Current State: What's Working

The demo is functional end-to-end for the READ path. All three Scene 5 questions confirmed working in Kiro:

| Question | Tool Called | Status |
|----------|-------------|--------|
| "What database are we using and why?" | `search-knowledge-facts` | ✅ confirmed — Aurora PostgreSQL with ACID rationale |
| "Catch me up on the last session" | `get-recent-conversations` + `list-sessions` + `search-knowledge-facts` | ✅ confirmed — sess-010 observability (CloudWatch, X-Ray, correlation IDs) |
| "What auth approach — JWT or opaque tokens?" | `search-knowledge-facts` | ✅ confirmed — JWT, opaque tokens rejected, gateway-level validation |

Elastic Agent Builder agent has:
- 4 tools (search-conversation-history, search-knowledge-facts, get-recent-conversations, list-sessions)
- 1 Skill: `checkout-memory-retrieval` — a runbook attached to the agent (visible in Kibana Skills tab)
- System instructions (always use memory tools first)

---

## Infrastructure

- **Elastic Cloud project:** `bedrock-memory-demo` (aws-us-east-1)
- **Kibana URL:** `https://bedrock-memory-demo-e86908.kb.us-east-1.aws.elastic.cloud`
- **Agent ID:** `checkout-service-memory`
- **3 indices:** `conversation-history` (40 docs), `knowledge-facts` (17 docs), `session-metadata` (10 docs)
- **Credentials:** in `.env` (gitignored) — never display

### Kiro setup (Jeff's machine)
- `~/.kiro/settings/mcp.json` — wired to Agent Builder MCP endpoint with Basic auth
- `~/.kiro/agents/checkout-memory.json` — Kiro agent Skill (global, available any project)
- Template in repo: `kiro-config/checkout-memory-agent.json`

---

## Demo Script: 7 Scenes

See full shot sheet: `demo_scripts/aws-summit-2026-navattic-shot-sheet.md`

| Scene | What It Shows | Status |
|-------|--------------|--------|
| 1 | Architecture diagram (Kiro → Bedrock + Kiro → Agent Builder) | Static slide |
| 2 | Kiro within-session memory (working memory) | No tools needed |
| 3 | Kiro new session — amnesia, no memory tools | Run from `~/repos/checkout-service-demo/` |
| 4 | Wire the memory: run `--add-mcp` script, show mcp.json before/after, Kiro Skill JSON, `/agent` picker | `--prep` to reset |
| 5 | Kiro with memory — Q1 DB, Q2 recent work (3 tools), Q3 auth | ✅ all 3 confirmed working |
| 6 | Kibana under the hood: agent config, tools, Skill, CALL agent via chat, Conversations log | Pre-record one Kibana chat session |
| 7 | Close / CTA slide | Static |

### Scene 5 question order (order is load-bearing)
Q1 must be DB (narrow — doesn't include auth), Q2 must be recent work (different tool), Q3 must be auth (not mentioned yet). If you ask "what stack?" first, auth appears in the response and Q3 won't fire a tool call.

### Scene 6 important note
Kiro calls MCP tools directly — those do NOT appear in Agent Builder's Conversations tab. The Conversations tab only shows calls via the Converse API (Kibana chat UI). Before recording Scene 6, open Kibana chat with `checkout-service-memory` and ask "What payment processor did we choose and why?" — this populates Conversations and validates the Skill is working.

---

## Setup / Reset Commands

```bash
# Full status check
python3 setup/demo-setup.py

# Re-seed all data (run within 2 weeks of recording so timestamps look recent)
python3 setup/demo-setup.py --reset

# Pre-recording prep (removes elastic-memory from mcp.json, resets checkout-service-demo README)
python3 setup/demo-setup.py --prep

# Restore elastic-memory to mcp.json (run before Scene 4 recording)
python3 setup/demo-setup.py --add-mcp

# Nuclear reset (deletes + recreates indices)
python3 setup/demo-setup.py --nuclear
```

Kiro must be restarted after `--prep` and `--add-mcp`.

---

## OPEN ISSUE: No Write Path (Critical Gap)

**Problem:** The demo currently only shows READ from memory. Kiro sessions don't write anything back to Elasticsearch. The 67 seeded documents are pre-populated — there's no demonstration of memory actually being built up. This looks like a RAG demo, not a memory demo.

**What's needed:** A `save-knowledge-fact` tool that writes a new document to the `knowledge-facts` index, exposed via Agent Builder (and therefore via MCP to Kiro).

**What we know:**
- Elastic Workflows support `elasticsearch.index` step to write documents to any index
- Agent Builder supports a `workflow` tool type that triggers an Elastic Workflow
- Workflow inputs are auto-detected from the YAML `inputs` block
- Via MCP, Kiro gets this tool too — write path: Kiro → MCP → Agent Builder → Workflow → ES

**What's NOT resolved:**
- The exact Elastic Workflow YAML structure for an `inputs` block + `elasticsearch.index` step
- Whether workflows can be created programmatically via REST API (vs Kibana UI only)
- The exact Agent Builder API payload for a `workflow` type tool
- The workflow_id format needed to reference a workflow in an Agent Builder tool

**Proposed demo flow once write is implemented:**
1. Scene 5 new beat OR Scene 6 Kiro beat: "We've decided to use Cloudflare CDN, 5-minute TTL for static assets. Save this to memory."
2. `save-knowledge-fact` tool fires → workflow runs → document written to `knowledge-facts`
3. Follow-up (new Kiro session): "What CDN are we using?" → `search-knowledge-facts` → retrieves Cloudflare decision
4. This proves memory isn't pre-seeded magic — it's whatever you tell it

**Next step:** Open Kibana → Workflows, create a test workflow with an input and an `elasticsearch.index` step, note the workflow ID format and YAML structure. Then wrap it as an Agent Builder tool and test via Kiro.

---

## Key Files

| File | Purpose |
|------|---------|
| `setup/create-agent.py` | Creates Agent Builder agent, tools, Skill (idempotent) |
| `setup/demo-setup.py` | Status check, reset, prep, add-mcp commands |
| `setup/create-indices.py` | Creates 3 ES indices with Jina semantic_text |
| `demo-data/seed.py` | Seeds 67 documents across 10 sessions |
| `kiro-config/checkout-memory-agent.json` | Kiro agent Skill template (copy to `~/.kiro/agents/`) |
| `kiro-config/mcp-servers.json` | MCP server template (copy to `~/.kiro/settings/mcp.json`) |
| `demo_scripts/aws-summit-2026-navattic-shot-sheet.md` | Scene-by-scene recording guide |
| `demo_scripts/aws-summit-2026-practice-guide.md` | 60-min stage practice script |

---

## Key Technical Decisions (don't reverse these)

- **Jina embeddings, NOT ELSER** — `semantic_text` field uses `.jina-embeddings-v5-text-small`
- **Basic auth for Kibana REST API** — ES-level API keys don't work against Kibana's REST layer
- **`params: {}` required** on ES|QL tools in Agent Builder (even with no params)
- **`Accept: application/json` required** on MCP calls or Agent Builder returns 406
- **No DynamoDB mentions anywhere** — at AWS Summit, competing against AWS products is a bad look. PostgreSQL is framed positively (ACID, JOINs, Serverless v2), never "chosen over DynamoDB"
- **Scene 5 question order is load-bearing** — narrow DB question first, then recent work, then auth. Broad "what stack?" question ruins Q3 tool call.
- **Kiro MCP = tool calls only, not Converse API** — Kiro sessions don't appear in Agent Builder Conversations tab

---

## Still To Do (before June 17)

- [ ] **Write path** — create Elastic Workflow + `save-knowledge-fact` Agent Builder tool (see Open Issue above)
- [ ] Navattic recording (Jeff records, after write path is resolved)
- [ ] Make GitHub repo public
- [ ] Blog post: "Building Memory-as-a-Service for AI Agents with Elastic and Amazon Bedrock"
- [ ] Uday sync — Bedrock creds for blog code examples
- [ ] Rehearsal (60 min out loud, before June 15)
