# elastic-bedrock-memory — AWS Summit NYC 2026

**Talk:** From Stateless to Stateful: Architecting Agent Memory with Elastic and Bedrock
**Event:** AWS Summit NYC, June 17, 2026 (60 min solo)
**Audience:** Builders/developers — wants repo + blog CTA
**Collaborator:** Uday (Elastic SA, AWS-focused) — needs sync for Bedrock creds for blog code examples

---

## What's Built

| Asset | Status | Location |
|---|---|---|
| Elastic Cloud project `bedrock-memory-demo` (aws-us-east-1) | ✅ live | cloud.elastic.co |
| 3 ES indices with Jina v5 `semantic_text` | ✅ live | conversation-history, knowledge-facts, session-metadata |
| 67 seeded docs (10 checkout service dev sessions) | ✅ live | `demo-data/seed.py` |
| Agent Builder agent + 5 MCP tools (4 read + 1 write) | ✅ live | Kibana → Agent Builder |
| Kiro MCP wired globally | ✅ | `~/.kiro/settings/mcp.json` |
| Kiro agent config (Skill) | ✅ | `kiro-config/checkout-memory-agent.json` |
| Semantic search verified end-to-end | ✅ | refund decisions retrieved correctly |
| Checkout service demo codebase | ✅ | `~/repos/checkout-service-demo` (separate repo) |
| GitHub repo (private) | ✅ | github.com/jeffvestal/elastic-bedrock-memory |
| Slide deck (22 slides, work copy) | ✅ | id `151FhokgExhlNBw1FuqPwyYVWVvlyKHfAJVBUiYUYUK4` |
| Demo run-book | ✅ | `demo_scripts/aws-summit-2026-demo-runbook.md` |
| FAQ-as-content script | ✅ | `demo_scripts/aws-summit-2026-faq.md` |
| Reference refund implementations | ✅ | `demo_scripts/reference/refunds-correct.py`, `refunds-amnesiac.py` |
| Navattic shot sheet | ✅ | `demo_scripts/aws-summit-2026-navattic-shot-sheet.md` |
| Practice guide (60 min stage script) | ✅ | `demo_scripts/aws-summit-2026-practice-guide.md` |

## Still To Do

- [ ] Make GitHub repo public (before June 17)
- [ ] New AWS-specific blog post ("Building Memory-as-a-Service for AI Agents with Elastic and Amazon Bedrock")
- [ ] Navattic demo recording (Jeff records)
- [ ] Uday sync — Bedrock creds for blog code examples
- [ ] Rehearsal (60 min out loud, before June 15)

---

## Infrastructure

### Credentials
Live in `/Users/jeffvestal/repos/elastic-bedrock-memory/.env` (gitignored).
- `ELASTICSEARCH_URL`, `ELASTICSEARCH_API_KEY` — for ES operations
- `KIBANA_URL`, `KIBANA_USER`, `KIBANA_PASSWORD` — for Kibana REST API (setup scripts)
- Do NOT display credentials in chat

### Kibana / Agent Builder
- Agent: `checkout-service-memory`
- 5 tools: `search-conversation-history`, `search-knowledge-facts`, `get-recent-conversations`, `list-sessions`, `save-knowledge-fact` (write)
- MCP endpoint: `{KIBANA_URL}/api/agent_builder/mcp`
- Required headers: `Authorization: Basic ...`, `kbn-xsrf: true`, `Accept: application/json`

### Kiro MCP config (Jeff's machine)
- `~/.kiro/settings/mcp.json` — already wired with Basic auth
- Template for repo users: `kiro-config/mcp-servers.json`

---

## Key Technical Decisions

- **No custom MCP server** — Agent Builder's native MCP endpoint is the MCP server
- **Jina embeddings, not ELSER** — `semantic_text` field type defaults to `.jina-embeddings-v5-text-small`; never say ELSER
- **Basic auth for Kibana REST API** — ES-level API keys don't authenticate against Kibana's REST layer; use `KIBANA_USER`/`KIBANA_PASSWORD` in setup scripts
- **`params: {}` required** — ES|QL tools in Agent Builder need explicit empty params object even with no params
- **`Accept: application/json` required** — MCP calls to Agent Builder 406 without it
- **No DynamoDB mentions anywhere** — at AWS Summit, competing against AWS products is a bad look

---

## Repo Structure

```
setup/
  create-indices.py    # Creates 3 ES indices with Jina semantic_text
  create-agent.py      # Creates Agent Builder agent + 5 tools (4 read + 1 write, idempotent)
demo-data/
  seed.py              # Seeds 67 docs across 10 checkout service sessions
kiro-config/
  mcp-servers.json              # Template Kiro MCP config (placeholder values)
  checkout-memory-agent.json    # Kiro agent config / Skill (copy to ~/.kiro/agents/)
demo_scripts/
  aws-summit-2026-demo-runbook.md          # THE capture run-book (exact prompts, slips, resets)
  aws-summit-2026-faq.md                   # FAQ-as-content (6 questions, 6-min segment)
  aws-summit-2026-navattic-shot-sheet.md   # Click-by-click Navattic recording guide
  aws-summit-2026-practice-guide.md        # 60-min stage practice script
  reference/
    refunds-correct.py    # Act 2 target: correct refund impl (int cents, idempotency, JWT)
    refunds-amnesiac.py   # Act 1 anti-pattern: wrong version Kiro writes without memory
docs/                  # Architecture diagrams (TBD)

# Separate codebase (NOT in this repo):
~/repos/checkout-service-demo   # Real FastAPI checkout service; baseline committed for
                                 # git checkout . resets between takes
```

---

## Demo Scenario

The demo is a ~30-min live narrative built around ONE coding task: **add a refund endpoint** to a real FastAPI checkout service (`~/repos/checkout-service-demo`). The seeded 10 sessions (~2 weeks of history) contain the decisions that make the demo land:

- Money = integer cents (sess-005) — float math caused a real production bug
- JWT auth on every route (sess-002) — opaque tokens rejected for introspection latency
- Stripe idempotency key on every charge (sess-004/007) — retry = double-charge without it
- Aurora PostgreSQL (sess-001) — ACID transactions for payment integrity
- Recent work (sess-010) — CloudWatch/X-Ray observability

**Act 1 (amnesiac Kiro, ~6 min):** Stock Kiro builds the refund endpoint wrong — reintroduces the float-money bug, skips the Stripe idempotency key, skips JWT auth, skips a double-refund guard. Developer corrects each by hand. Breaking point: "every one of those corrections is something my team already decided."

**Live-build (~10 min):** On stage: `create-indices.py` (shows semantic_text mapping), `create-agent.py` (tools via REST API), `seed.py` (loads 2 weeks of history). Full memory system built in ~10 min.

**Wire (~3 min):** `--add-mcp` adds the elastic-memory block to mcp.json. Open `checkout-memory.json` Skill. Restart Kiro, `/agent` → checkout-memory.

**Act 2 (memory-wired Kiro, ~7 min):** SAME verbatim prompt. Kiro calls `search-knowledge-facts` first, writes the refund endpoint **correctly, first pass**, citing the sessions. New decision (90-day refund window, partial-refund cap) is then saved via `save-knowledge-fact`.

**Act 3 (~4 min):** Fresh session / "teammate" reads back the saved refund policy via `search-knowledge-facts`. Kibana Conversations tab shows the audit trail.

### Demo questions that work (Act 2 + Act 3)
- Verbatim refund prompt → Kiro calls `search-knowledge-facts` before writing any code
- `search-knowledge-facts` retrieves: integer cents, Stripe idempotency, JWT, Aurora rationale
- "What's our refund policy?" (new session) → `search-knowledge-facts` → 90-day / partial-cap fact saved in Act 2

---

## Next Session Priority

**Blog post** — "Building Memory-as-a-Service for AI Agents with Elastic and Amazon Bedrock"

Structure:
1. Hook: the amnesia problem
2. Architecture overview + diagram
3. Index design (code: mapping JSON)
4. Agent Builder setup (code: REST API calls from create-agent.py)
5. MCP wiring (code: mcp-servers.json)
6. End-to-end walkthrough (references demo)
7. Design decisions and tradeoffs
8. CTA: repo link + link to existing Search Labs memory blog
