"""
Create the Elastic Agent Builder agent with memory tools for the demo.
Run: python setup/create-agent.py
Requires KIBANA_URL and KIBANA_API_KEY in .env (or set KIBANA_USER + KIBANA_PASSWORD for admin setup).
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

KIBANA_URL = os.environ["KIBANA_URL"].rstrip("/")

# Support both API key and username/password auth
# Prefer username/password if set (needed for initial setup — Kibana REST API requires Kibana-native key or basic auth)
session = requests.Session()
session.headers.update({"Content-Type": "application/json", "kbn-xsrf": "true", "Accept": "application/json"})
if os.environ.get("KIBANA_USER") and os.environ.get("KIBANA_PASSWORD"):
    session.auth = (os.environ["KIBANA_USER"], os.environ["KIBANA_PASSWORD"])
elif os.environ.get("KIBANA_API_KEY"):
    session.headers["Authorization"] = f"ApiKey {os.environ['KIBANA_API_KEY']}"
else:
    raise ValueError("Set KIBANA_USER+KIBANA_PASSWORD or KIBANA_API_KEY in .env")


TOOLS = [
    {
        "id": "search-conversation-history",
        "type": "index_search",
        "description": "Search past conversation history and developer discussions using semantic search. Use this to recall what was discussed, decided, or worked on in previous development sessions.",
        "tags": ["memory", "search", "conversation"],
        "configuration": {"pattern": "conversation-history"},
    },
    {
        "id": "search-knowledge-facts",
        "type": "index_search",
        "description": "Search architectural decisions, technical choices, bug fixes, and key facts from past sessions. Use this when asked about which database, auth approach, API design, payment processor, or any other decision was made.",
        "tags": ["memory", "search", "decisions"],
        "configuration": {"pattern": "knowledge-facts"},
    },
    {
        "id": "get-recent-conversations",
        "type": "esql",
        "description": "Retrieve the most recent conversation turns across all sessions to see what was last worked on.",
        "tags": ["memory", "recent"],
        "configuration": {
            "query": 'FROM `conversation-history` | SORT timestamp DESC | LIMIT 20 | KEEP session_id, timestamp, role, content, topic_tags',
            "params": {},
        },
    },
    {
        "id": "list-sessions",
        "type": "esql",
        "description": "List all past development sessions with their summaries and topics — useful to understand what phases of the project have been covered.",
        "tags": ["memory", "sessions"],
        "configuration": {
            "query": "FROM `session-metadata` | SORT start_time DESC | KEEP session_id, start_time, summary, topics",
            "params": {},
        },
    },
]

AGENT = {
    "id": "checkout-service-memory",
    "name": "Checkout Service — Memory Agent",
    "description": "I have full memory of the checkout service project. Ask me about past decisions, bugs, architecture choices, or what we worked on in any session.",
    "labels": ["demo", "aws-summit", "memory"],
    "configuration": {
        "instructions": """You are a stateful AI development assistant with persistent memory of the checkout service project.

ALWAYS use your memory tools before answering questions about the project. Never say "I don't have access to previous conversations" — you do, via your tools.

When asked about:
- Technology/architecture choices → use search-knowledge-facts first
- Specific discussions or conversations → use search-conversation-history
- What was recently worked on → use get-recent-conversations
- What sessions have happened → use list-sessions

Always cite your source: "Based on our session from [date], we decided..." or "According to the architectural decision recorded in session [id]..."

This is the entire point: you are NOT stateless. You remember everything because Elasticsearch is your memory.""",
        "tools": [
            {
                "tool_ids": [
                    "search-conversation-history",
                    "search-knowledge-facts",
                    "get-recent-conversations",
                    "list-sessions",
                    "platform.core.search",
                ]
            }
        ],
    },
}


def upsert_tool(tool):
    resp = session.post(f"{KIBANA_URL}/api/agent_builder/tools", json=tool)
    if resp.status_code in (200, 201):
        tid = resp.json().get("id", tool["id"])
        print(f"  ✓ {tool['id']}: created")
        return tid
    elif resp.status_code in (409, 400) and "already exists" in resp.text:
        # Update existing tool
        resp2 = session.put(f"{KIBANA_URL}/api/agent_builder/tools/{tool['id']}", json=tool)
        if resp2.status_code in (200, 201):
            print(f"  ~ {tool['id']}: updated")
        else:
            print(f"  ~ {tool['id']}: already exists (skipped)")
        return tool["id"]
    else:
        print(f"  ✗ {tool['id']}: {resp.status_code} {resp.text[:200]}")
        return tool["id"]


def upsert_agent(agent):
    resp = session.post(f"{KIBANA_URL}/api/agent_builder/agents", json=agent)
    if resp.status_code in (200, 201):
        aid = resp.json().get("id", agent["id"])
        print(f"  ✓ Agent: {aid}")
        return aid
    elif resp.status_code == 409:
        # Update existing
        resp2 = session.put(f"{KIBANA_URL}/api/agent_builder/agents/{agent['id']}", json=agent)
        if resp2.status_code in (200, 201):
            print(f"  ~ Agent updated: {agent['id']}")
        else:
            print(f"  ✗ Agent update failed: {resp2.status_code} {resp2.text[:200]}")
        return agent["id"]
    else:
        print(f"  ✗ Agent: {resp.status_code} {resp.text[:300]}")
        return None


if __name__ == "__main__":
    print("Creating Agent Builder tools...")
    for tool in TOOLS:
        upsert_tool(tool)

    print("\nCreating Agent Builder agent...")
    agent_id = upsert_agent(AGENT)

    if agent_id:
        print(f"\n✅ Setup complete.")
        print(f"   Agent ID: {agent_id}")
        print(f"   Test in Kibana: {KIBANA_URL}/app/chat")
        print(f"   MCP endpoint:   {KIBANA_URL}/api/agent_builder/mcp")
        print(f"\n   Kiro MCP config (kiro-config/mcp-servers.json):")
        print(f"   URL: {KIBANA_URL}/api/agent_builder/mcp")
