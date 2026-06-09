"""
Create the Elastic Agent Builder agent with memory tools for the demo.
Run: python setup/create-agent.py
Requires KIBANA_URL and KIBANA_API_KEY in .env (or set KIBANA_USER + KIBANA_PASSWORD for admin setup).
Run setup/validate-write-path.py first to create the workflow and write WORKFLOW_ID to .env.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

KIBANA_URL = os.environ["KIBANA_URL"].rstrip("/")
WORKFLOW_ID = os.environ.get("WORKFLOW_ID")  # set by validate-write-path.py

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

# Workflow write tool — only added if WORKFLOW_ID is set (run validate-write-path.py first)
WRITE_TOOL = {
    "id": "save-knowledge-fact",
    "type": "workflow",
    "description": "Save a new architectural decision or technical fact to long-term memory. Use when the user confirms a technology choice, documents a decision, or wants to remember something important about the project. Provide the fact as a complete sentence including the rationale.",
    "tags": ["memory", "write", "decisions"],
    "configuration": {
        "workflow_id": WORKFLOW_ID,
    },
} if WORKFLOW_ID else None

SKILL = {
    "id": "checkout-memory-retrieval",
    "name": "Checkout Service Memory Retrieval",
    "description": "Runbook for recalling project decisions and history from Elasticsearch. Use when asked about architecture choices, past discussions, or recent work.",
    "content": """## When to Use This Skill

Use this skill when the user asks about:
- Technology or architecture choices (database, auth, payments, deployment)
- Past decisions and why they were made
- What was recently worked on or what happened in a session
- An overview of all development sessions

## Memory Retrieval Process

### For architectural decisions and tech choices
Use `search-knowledge-facts` with the user's question as the natural language query.
Return the decision, the rationale, and the session it came from.

### For specific past discussions
Use `search-conversation-history` to find relevant conversation turns.
Summarize what was discussed and any conclusions reached.

### For recent work and session recap
Use `get-recent-conversations` — ES|QL query returning the most recent turns.
Summarize the last session's focus and key outcomes.

### For a full session overview
Use `list-sessions` to show all sessions with summaries and topics.

## Always cite your source
Format: "Based on session [id] from [date], we decided..."
Never answer from training data when memory tools are available.""",
    "tool_ids": [
        "search-conversation-history",
        "search-knowledge-facts",
        "get-recent-conversations",
        "list-sessions",
    ] + (["save-knowledge-fact"] if WORKFLOW_ID else []),
}

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
- Saving a decision or fact → use save-knowledge-fact (include the full decision and rationale)

Always cite your source: "Based on our session from [date], we decided..." or "According to the architectural decision recorded in session [id]..."

This is the entire point: you are NOT stateless. You remember everything because Elasticsearch is your memory.""",
        "tools": [
            {
                "tool_ids": [
                    "search-conversation-history",
                    "search-knowledge-facts",
                    "get-recent-conversations",
                    "list-sessions",
                ] + (["save-knowledge-fact"] if WORKFLOW_ID else [])
            }
        ],
        "skill_ids": ["checkout-memory-retrieval"],
    },
}


def upsert_skill(skill):
    resp = session.post(f"{KIBANA_URL}/api/agent_builder/skills", json=skill)
    if resp.status_code in (200, 201):
        print(f"  ✓ {skill['id']}: created")
        return skill["id"]
    elif resp.status_code in (409, 400) and "already exists" in resp.text:
        body = {k: v for k, v in skill.items() if k != "id"}
        resp2 = session.put(f"{KIBANA_URL}/api/agent_builder/skills/{skill['id']}", json=body)
        if resp2.status_code in (200, 201):
            print(f"  ~ {skill['id']}: updated")
        else:
            print(f"  ~ {skill['id']}: already exists (skipped)")
        return skill["id"]
    else:
        print(f"  ✗ {skill['id']}: {resp.status_code} {resp.text[:200]}")
        return skill["id"]


def upsert_tool(tool):
    resp = session.post(f"{KIBANA_URL}/api/agent_builder/tools", json=tool)
    if resp.status_code in (200, 201):
        tid = resp.json().get("id", tool["id"])
        print(f"  ✓ {tool['id']}: created")
        return tid
    elif resp.status_code in (409, 400) and "already exists" in resp.text:
        # Update existing tool — PUT does not accept 'id' in body
        body = {k: v for k, v in tool.items() if k != "id"}
        resp2 = session.put(f"{KIBANA_URL}/api/agent_builder/tools/{tool['id']}", json=body)
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
    elif resp.status_code in (409, 400) and "already exists" in resp.text:
        # Update existing — PUT does not accept 'id' in body
        body = {k: v for k, v in agent.items() if k != "id"}
        resp2 = session.put(f"{KIBANA_URL}/api/agent_builder/agents/{agent['id']}", json=body)
        if resp2.status_code in (200, 201):
            print(f"  ~ Agent updated: {agent['id']}")
        else:
            print(f"  ✗ Agent update failed: {resp2.status_code} {resp2.text[:200]}")
        return agent["id"]
    else:
        print(f"  ✗ Agent: {resp.status_code} {resp.text[:300]}")
        return None


if __name__ == "__main__":
    if not WORKFLOW_ID:
        print("⚠️  WORKFLOW_ID not set in .env — skipping save-knowledge-fact tool.")
        print("   Run:  python setup/validate-write-path.py  to create the workflow first.")
        print()

    print("Creating Agent Builder skill...")
    upsert_skill(SKILL)

    print("\nCreating Agent Builder tools...")
    all_tools = TOOLS + ([WRITE_TOOL] if WRITE_TOOL else [])
    for tool in all_tools:
        upsert_tool(tool)

    print("\nCreating Agent Builder agent...")
    agent_id = upsert_agent(AGENT)

    if agent_id:
        tool_count = len(all_tools)
        print(f"\n✅ Setup complete.")
        print(f"   Agent ID: {agent_id}")
        print(f"   Tools: {tool_count} ({'read + write' if WRITE_TOOL else 'read only — run validate-write-path.py to enable write'})")
        print(f"   Test in Kibana: {KIBANA_URL}/app/chat")
        print(f"   MCP endpoint:   {KIBANA_URL}/api/agent_builder/mcp")
        print(f"\n   Kiro MCP config (kiro-config/mcp-servers.json):")
        print(f"   URL: {KIBANA_URL}/api/agent_builder/mcp")
