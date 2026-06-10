# Handoff: elastic-bedrock-memory Demo — AWS Summit NYC 2026

**Date:** 2026-06-10
**Talk:** From Stateless to Stateful: Architecting Agent Memory with Elastic and Bedrock
**Event:** AWS Summit NYC, June 17, 2026
**Repo:** github.com/jeffvestal/elastic-bedrock-memory (currently private — make public before June 17)

---

## Current State: What's Working

### Read path — fully confirmed

| Question | Tool Called | Status |
|----------|-------------|--------|
| "What database are we using and why?" | `search-knowledge-facts` | ✅ Aurora PostgreSQL with ACID rationale |
| "Catch me up on the last session" | `get-recent-conversations` + `list-sessions` + `search-knowledge-facts` | ✅ sess-010 observability (CloudWatch, X-Ray, correlation IDs) |
| "What auth approach — JWT or opaque tokens?" | `search-knowledge-facts` | ✅ JWT, opaque tokens rejected, gateway-level validation |

### Write path — implemented, NOT yet live-tested through Kiro

- `save-knowledge-fact` workflow tool is created in Agent Builder (tool id: `save-knowledge-fact`)
- Backed by Elastic Workflow id `save-knowledge-fact-3` in Kibana
- Workflow YAML: `elasticsearch.request` POST to `/knowledge-facts/_doc?refresh=wait_for`
- Jina inference on write confirmed: `fact_semantic` populates when doc is written directly to ES ✅
- Agent has **5 tools** (4 read + 1 write), `python3 setup/demo-setup.py` shows all green ✅
- **One open risk:** Workflow was created with `valid: False` and `definition: null` in Kibana's API response — unknown if this blocks execution when triggered via Agent Builder tool call. Needs live Kiro test.

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
| 1 | Architecture diagram | Static slide |
| 2 | Kiro within-session memory | No tools needed |
| 3 | Kiro new session — amnesia | Run from `~/repos/checkout-service-demo/` |
| 4 | Wire the memory: `--add-mcp`, show mcp.json before/after, Kiro Skill, `/agent` picker | `--prep` to reset |
| 5 | Kiro with memory — Q1 DB, Q2 recent work, Q3 auth, Q4 save CDN, Q4b read-back | Q1-Q3 ✅ confirmed; Q4/Q4b needs live test |
| 6 | Kibana: agent config, tools, Skill, chat reads what Kiro wrote | Needs Q4 confirmed first |
| 7 | Close / CTA slide | Static |

### Scene 5 question order (load-bearing for Q1-Q3)
Q1 must be DB (narrow), Q2 must be recent work (different tool), Q3 must be auth (not mentioned yet).
Q4 write beat: "We've decided to use Cloudflare CDN with a 5-minute TTL. Save this to memory."
Q4b: fresh Kiro session → "What CDN are we using?" → should retrieve Cloudflare.

---

## Setup Commands (single entry point)

```bash
# Status check
python3 setup/demo-setup.py

# First-time setup (creates Elastic Workflow + Agent Builder agent with write tool)
python3 setup/demo-setup.py --setup

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

## OPEN ISSUE: Verify Write Path End-to-End (MUST DO BEFORE RECORDING)

**What to test:**
1. In Kiro with checkout-memory agent active, say: "We've decided to use Cloudflare CDN with a 5-minute TTL for static assets. Save this to memory."
2. Confirm `save-knowledge-fact` tool fires in Kiro's tool call output
3. Run `python3 setup/demo-setup.py` — `knowledge-facts` count should be 18 (one new doc)
4. Start a **new** Kiro session, ask: "What CDN are we using?"
5. `search-knowledge-facts` should fire and return Cloudflare

**If the tool fires but no doc appears:** The Elastic Workflow has `valid: False` / `definition: null` — the workflow isn't executing. Fix path:
- Option A: Recreate the workflow via Kibana UI, note the YAML it generates, use that as the template
- Option B: Switch to the insurance sidecar (`mcp-sidecar/save-fact-server.py`) for Kiro-only write path; adjust Scene 6 to not show Agent Builder reading Kiro's write

**If the tool doesn't fire at all:** Agent Builder isn't passing the workflow tool over MCP — check that `save-knowledge-fact` appears in Kiro's `/mcp list`.

---

## Remaining Work Before June 17

- [ ] **Live Kiro test of write beat** — verify save-knowledge-fact fires and doc reads back cross-session
- [ ] Navattic recording (Jeff records, after write path verified)
- [ ] Make GitHub repo public
- [ ] Blog post: "Building Memory-as-a-Service for AI Agents with Elastic and Amazon Bedrock"
- [ ] Uday sync — Bedrock creds for blog code examples
- [ ] Rehearsal (60 min out loud, before June 15)

---

## Key Files

| File | Purpose |
|------|---------|
| `setup/demo-setup.py` | Single entry point: status, --setup, --reset, --prep, --add-mcp, --nuclear |
| `setup/validate-write-path.py` | Creates Elastic Workflow, tests Jina inference on write, writes WORKFLOW_ID to .env |
| `setup/create-agent.py` | Creates Agent Builder agent, tools (read + write), Skill |
| `setup/create-indices.py` | Creates 3 ES indices with Jina semantic_text |
| `demo-data/seed.py` | Seeds 67 documents across 10 sessions |
| `mcp-sidecar/save-fact-server.py` | Insurance: local MCP server write path (Kiro-only fallback if workflow fails) |
| `kiro-config/checkout-memory-agent.json` | Kiro agent Skill template (copy to `~/.kiro/agents/`) |
| `kiro-config/mcp-servers.json` | MCP server template (copy to `~/.kiro/settings/mcp.json`) |
| `demo_scripts/aws-summit-2026-navattic-shot-sheet.md` | Scene-by-scene recording guide (updated with Q4 write beat) |
| `demo_scripts/aws-summit-2026-practice-guide.md` | 60-min stage practice script |

---

## Key Technical Decisions (don't reverse these)

- **Jina embeddings, NOT ELSER** — `semantic_text` field uses `.jina-embeddings-v5-text-small`
- **`fact_semantic` must be set explicitly on write** — it is NOT copied from `fact` automatically; both fields must be set to the same text value when indexing
- **Basic auth for Kibana REST API** — ES-level API keys don't work against Kibana's REST layer
- **`params: {}` required** on ES|QL tools in Agent Builder (even with no params)
- **`Accept: application/json` required** on MCP calls or Agent Builder returns 406
- **No DynamoDB mentions anywhere** — at AWS Summit, competing against AWS products is a bad look
- **Scene 5 question order is load-bearing** — narrow DB question first, then recent work, then auth
- **Kiro MCP = tool calls only, not Converse API** — Kiro sessions don't appear in Agent Builder Conversations tab; verify writes via ES doc count, not Conversations UI
- **Elastic Workflow API payload:** `{"workflows": [{"yaml": "..."}]}` (array wrapper required); response shape: `{"created": [...], "failed": [...]}`
