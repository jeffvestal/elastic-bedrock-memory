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
| Agent Builder agent + 4 MCP tools | ✅ live | Kibana → Agent Builder |
| Kiro MCP wired globally | ✅ | `~/.kiro/settings/mcp.json` |
| Semantic search verified end-to-end | ✅ | "which DB did we choose?" → correct answer |
| GitHub repo (private) | ✅ | github.com/jeffvestal/elastic-bedrock-memory |
| Slide deck (26 slides, Google Slides) | ✅ | see kuchi-kopi project file for link |
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
- 4 tools: `search-conversation-history`, `search-knowledge-facts`, `get-recent-conversations`, `list-sessions`
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

---

## Repo Structure

```
setup/
  create-indices.py    # Creates 3 ES indices with Jina semantic_text
  create-agent.py      # Creates Agent Builder agent + 4 tools (idempotent)
demo-data/
  seed.py              # Seeds 67 docs across 10 checkout service sessions
kiro-config/
  mcp-servers.json     # Template Kiro MCP config (placeholder values)
demo_scripts/
  aws-summit-2026-navattic-shot-sheet.md   # Click-by-click Navattic recording guide
  aws-summit-2026-practice-guide.md        # 60-min stage practice script
docs/                  # Architecture diagrams (TBD)
```

---

## Demo Scenario

Developer building a checkout service over 10 sessions (~2 weeks). Seeded data includes:
- DB choice: Aurora PostgreSQL (DynamoDB eliminated — eventual consistency failed cart totals)
- Auth: JWT with refresh tokens (OAuth considered, eliminated — complexity)
- Payment: Stripe (Braintree considered, eliminated — SDK quality)
- Recent work (session 10): Stripe webhook handler, idempotency keys

Demo questions that work:
- "Which database did we choose and why?" → `search-knowledge-facts` → PostgreSQL/Aurora
- "What auth approach did we decide on?" → `search-knowledge-facts` → JWT
- "What did we work on in the last session?" → `get-recent-conversations` → Stripe webhook

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
