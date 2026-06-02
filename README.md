# Elastic + Amazon Bedrock: Memory-as-a-Service for AI Agents

> **Talk**: From Stateless to Stateful: Architecting Agent Memory with Elastic and Bedrock  
> **Event**: AWS Summit NYC, June 17, 2026

Generative AI's biggest bottleneck is amnesia. This repo shows how to build a **Memory-as-a-Service** layer using Elasticsearch as the persistent memory store, Elastic Agent Builder to expose memory as tools, and Kiro (with Amazon Bedrock) as the agentic IDE.

## Architecture

```
Kiro CLI (Amazon Bedrock)
    └─ MCP → Elastic Agent Builder (/api/agent_builder/mcp)
                  └─ search_conversation_history  (semantic search)
                  └─ search_knowledge_facts        (semantic search)
                  └─ get_recent_session            (ES|QL)
                  └─ list_sessions                 (ES|QL)
            Elasticsearch (backend)
                  └─ conversation-history index
                  └─ knowledge-facts index
                  └─ session-metadata index
```

## Quickstart

### 1. Set up Elastic Cloud

Create a free Elastic Cloud account at [elastic.co/cloud](https://elastic.co/cloud) and spin up an Elasticsearch Serverless project.

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Elasticsearch URL, Kibana URL, and API keys
```

### 3. Install dependencies

```bash
pip install -r setup/requirements.txt
```

### 4. Create indices

```bash
python setup/create-indices.py
```

### 5. Seed demo data

```bash
python demo-data/seed.py
```

### 6. Create the Agent Builder agent

```bash
python setup/create-agent.py
```

### 7. Connect Kiro

Copy `kiro-config/mcp-servers.json` to your project's `.kiro/` directory (or merge into existing MCP config). Set `KIBANA_URL` and `KIBANA_API_KEY` from your `.env`.

### 8. Ask Kiro about your project history

```
"What database did we decide to use and why?"
"What was the auth approach we settled on?"
"Were there any significant bugs we fixed?"
```

## Blog Post

[Building Memory-as-a-Service for AI Agents with Elastic and Amazon Bedrock](#) ← coming soon

## Related

- [Your search index is already an agent memory system](https://www.elastic.co/search-labs) — deeper dive into Elasticsearch as agent memory
- [Elastic Agent Builder docs](https://www.elastic.co/docs)
- [Kiro](https://kiro.dev) — agentic IDE powered by Amazon Bedrock
