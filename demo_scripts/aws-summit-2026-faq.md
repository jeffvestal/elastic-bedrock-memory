---
type: final
title: "AWS Summit NYC 2026 — FAQ Section"
status: active
category: content
priority: high
created: 2026-06-10
updated: 2026-06-10
tags: [aws-summit-2026, faq, talk, elastic-bedrock-memory]
---

# AWS Summit NYC 2026 — FAQ Section

**Talk:** From Stateless to Stateful: Architecting Agent Memory with Elastic and Bedrock
**Section:** Q&A / FAQ-as-content
**Timing:** ~6 minutes — expand or contract to fill remaining time after core Q&A.

---

## FAQ Questions

---

**"I don't use Kiro — does this work with my IDE or agent?"**

Absolutely. Kiro is the IDE in this demo because it runs on Bedrock and wires cleanly into the AWS story. But the integration point isn't Kiro — it's the MCP endpoint. Cursor, Claude Code, Windsurf, a custom agent you built yourself — if it speaks MCP, it connects to the same memory store. You swap the IDE; you keep the architecture.

- The connection is three lines of JSON: URL (`/api/agent_builder/mcp`), an Authorization header, and two required request headers. That's it.
- The tools — semantic search, ES|QL, write — are exposed by Agent Builder. The IDE just calls them.
- For custom agents: the repo includes the MCP config template. Point it at your Kibana URL, drop in your credentials, wire it into whatever framework you're using.

---

**"What does this cost?"**

Two cost centers: Elastic Cloud for the memory store, Bedrock for inference. On the Elastic side, serverless means you pay for what you use — no provisioned nodes to size. The more interesting question is what this *saves*. A targeted semantic lookup reads a handful of documents — the most relevant facts from thousands of stored decisions. The alternative is stuffing all of that into a context window and paying to re-read every token on every forward pass. That's orders of magnitude more expensive per query, and it still has a ceiling.

- Elastic Cloud has a free trial at cloud.elastic.co. The full setup runs in minutes on the free tier.
- For production: cost scales with data volume and query rate, not model token count. Agent memory is a search workload, not an inference workload.
- The economics improve as your memory store grows. More stored knowledge, same cost per query — because you're retrieving, not re-reading.

---

**"Does this only work with Amazon Bedrock / AWS?"**

No. Bedrock is the inference engine in this demo — it's what Kiro uses to run the model. But Agent Builder's MCP endpoint doesn't know or care which LLM is on the other end. It exposes tools. Whatever speaks MCP can call those tools. GPT-4, Claude, Gemini, a local model — swap in any inference layer you want. The memory store stays the same.

- This was an explicit design goal: two separate paths. Bedrock handles inference. Elastic handles memory. Neither depends on the other's vendor.
- The composability is the point. You're not locked into a single-vendor AI stack. Add the memory layer once; reuse it with any model front-end.
- If you're not on AWS at all: Elastic Cloud runs on AWS, GCP, and Azure. Pick your region, deploy, wire it in.

---

**"Does it scale?"**

Elasticsearch is what enterprise teams run at billions of documents for search, logs, and observability. Agent memory is just another index. Millions of conversation turns, hundreds of agents, whole teams sharing one memory store — the infrastructure has been doing this at scale for years. Semantic search with Jina embeddings doesn't degrade as the index grows because it's doing vector similarity, not a full table scan.

- Hybrid retrieval — semantic plus BM25 — runs in milliseconds at scale. You get fuzzy recall and keyword precision in the same query.
- Multi-agent, multi-user: every agent on the team reads and writes the same store. Access scoped by API keys and Elasticsearch RBAC.
- The demo runs on a seeded dataset of 67 documents. Production teams have run the same pattern at millions of documents with no architectural change.

---

**"Is it secure, auditable, and governed?"**

Every agent call is logged in Kibana Conversations — what was queried, which tool was called, what documents were retrieved, what the model responded. That's your audit trail. Access is scoped with Elasticsearch API keys and RBAC: you control which agents can read which indices, and write access is a separate scope entirely. Data stays in the region where you deployed Elastic Cloud — your residency requirements follow your deployment, not ours.

- This is not a black box. If an agent retrieves the wrong fact or a bad decision propagates, you have a complete record of what happened and when.
- Tool-level access control: a read-only agent gets read-only tools. The save-knowledge-fact write tool requires explicit scope.
- Kibana Conversations works out of the box with Agent Builder. No extra logging infrastructure to stand up.

---

**"How does memory get written and maintained — does it grow forever, and what about stale or conflicting facts?"**

Memory is written explicitly — the agent proposes a fact, you confirm it, it goes in. It's not passively vacuuming your conversations. Every stored fact has a category and an importance score. When you make a new decision that supersedes an old one — say you switch databases — you store the new fact. Semantic search surfaces the most relevant and highest-importance results, so the current decision naturally wins. You're not buried in stale data; you're retrieving the closest match to what you just asked.

- The importance score is your primary governance knob. High-importance facts rank higher in retrieval even when semantic similarity is close.
- Stale facts don't disappear — they're still there as history — but they lose retrieval priority when a newer, more relevant fact exists. That's intentional: you get an audit trail and current-state accuracy.
- Memory hygiene is a design property, not an afterthought. The three-index schema (conversation turns, extracted facts, session metadata) keeps each type independently queryable and maintainable. You can prune conversation-history on a retention schedule without touching knowledge-facts.
