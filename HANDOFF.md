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

## Demo Structure: 5 Segments (~30 min live screen)

Narrative spine: ONE task — **add a refund endpoint** — built wrong by an amnesiac Kiro (Act 1), then built right by a memory-wired Kiro (Act 2), with the memory system built live in between.

Full talk structure: Intro+amnesia hook (slides, 5m) → Seg 2 Act 1 (6m) → Seg 3 live-build (10m) → Seg 4 wire (3m) → Seg 5 Act 2 (7m) → Seg 6 Act 3 (4m) → FAQ slides (6m) → recap (4m) → CTA (3m) → Q&A.

See `demo_scripts/aws-summit-2026-demo-runbook.md` for exact prompts, target slips, live-build command sequence, state matrix, and reset procedures.

| Segment | What It Shows | Status |
|---------|--------------|--------|
| 2 — Act 1 amnesia | Stock Kiro builds refunds **wrong**: float money, no idempotency key, no JWT, no double-refund guard. Developer corrects each. Breaking point: "every correction is something the team already decided." | Needs capture |
| 3 — live-build | `create-indices.py` (semantic_text), `create-agent.py` (tools via API), `seed.py` (67 docs). Memory system built on stage in ~10 min. | Needs capture |
| 4 — wire memory | `--add-mcp` (mcp.json before/after), Kiro Skill (`checkout-memory.json`), restart Kiro, `/agent` picker. | Needs capture |
| 5 — Act 2 memory | SAME prompt. Kiro calls `search-knowledge-facts` first, writes correct code citing sessions. New decision (90-day refund window, partial cap) saved via `save-knowledge-fact`. | Needs write-path verified |
| 6 — Act 3 | Fresh session / "teammate" reads back the saved refund policy. Kibana Conversations shows audit trail. | Needs Act 2 captured first |

### State matrix (what must be true at each segment)
| Segment | Elastic memory | Kiro agent | mcp.json | checkout-service-demo |
|---------|----------------|-----------|----------|-----------------------|
| 2 Act 1 | not wired | **stock** | no elastic-memory | baseline |
| 3 live-build | building on camera | n/a | n/a | n/a |
| 4 wire | populated | switching to checkout-memory | **adding** elastic-memory | baseline |
| 5 Act 2 | populated | **checkout-memory** | elastic-memory present | baseline (reset after Act 1) |
| 6 Act 3 | populated + 1 saved fact | checkout-memory | present | n/a |

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
- [ ] Navattic recording (Jeff records, following the new run-book — `demo_scripts/aws-summit-2026-demo-runbook.md`)
- [ ] Make GitHub repo public
- [ ] Blog post: "Building Memory-as-a-Service for AI Agents with Elastic and Amazon Bedrock"
- [ ] Uday sync — Bedrock creds for blog code examples
- [ ] Rehearsal (60 min out loud, before June 15)
- [x] Deck reshaped to 22 slides on a work copy (id `151FhokgExhlNBw1FuqPwyYVWVvlyKHfAJVBUiYUYUK4`) — original untouched
- [x] HANDOFF.md and CLAUDE.md updated to reflect redesigned demo

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
| `demo_scripts/aws-summit-2026-demo-runbook.md` | **THE capture run-book** — exact prompts, target slips, live-build commands, state matrix, reset procedures |
| `demo_scripts/aws-summit-2026-faq.md` | FAQ-as-content (6 questions, 6-min FAQ segment) |
| `demo_scripts/aws-summit-2026-navattic-shot-sheet.md` | Recording guide (follows the new run-book) |
| `demo_scripts/aws-summit-2026-practice-guide.md` | 60-min stage practice script |
| `demo_scripts/reference/refunds-correct.py` | Reference: correct refund implementation (Act 2 target) |
| `demo_scripts/reference/refunds-amnesiac.py` | Reference: wrong refund implementation (Act 1 anti-pattern) |
| `~/repos/checkout-service-demo` | **Separate repo** — real FastAPI checkout codebase with a refund-shaped hole; baseline committed for `git checkout .` resets |

---

## Key Technical Decisions (don't reverse these)

- **Jina embeddings, NOT ELSER** — `semantic_text` field uses `.jina-embeddings-v5-text-small`
- **`fact_semantic` must be set explicitly on write** — it is NOT copied from `fact` automatically; both fields must be set to the same text value when indexing
- **Basic auth for Kibana REST API** — ES-level API keys don't work against Kibana's REST layer
- **`params: {}` required** on ES|QL tools in Agent Builder (even with no params)
- **`Accept: application/json` required** on MCP calls or Agent Builder returns 406
- **No DynamoDB mentions anywhere** — at AWS Summit, competing against AWS products is a bad look
- **Kiro MCP = tool calls only, not Converse API** — Kiro sessions don't appear in Agent Builder Conversations tab; verify writes via ES doc count, not Conversations UI
- **Elastic Workflow API payload:** `{"workflows": [{"yaml": "..."}]}` (array wrapper required); response shape: `{"created": [...], "failed": [...]}`
