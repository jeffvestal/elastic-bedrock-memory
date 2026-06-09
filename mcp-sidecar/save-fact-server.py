"""
Insurance sidecar MCP server for the write path.

PURPOSE: Fallback if the Elastic Workflow / Agent Builder workflow tool path fails at rehearsal.
         This server exposes save-knowledge-fact as a local MCP tool that writes directly to ES.

IMPORTANT: This is PARKED — do not wire it into the demo unless the workflow tool fails.

         If used:
         1. Add to ~/.kiro/settings/mcp.json alongside (or instead of) elastic-memory:
               "save-fact-sidecar": {
                 "command": "python",
                 "args": ["/path/to/elastic-bedrock-memory/mcp-sidecar/save-fact-server.py"],
                 "env": {"ELASTICSEARCH_URL": "...", "ELASTICSEARCH_API_KEY": "..."}
               }
         2. Update checkout-memory-agent.json to use @save-fact-sidecar/save-knowledge-fact
         3. Restart Kiro

TRADEOFF vs. workflow tool: This only covers Kiro. The Agent Builder chat UI will NOT see
the write — the write goes direct to ES, bypassing Agent Builder entirely.
This means Scene 6 "Agent Builder chat reads Kiro's write" beat won't work.
Adjust Scene 6 to show Agent Builder reading pre-seeded memory only.

Usage:
  python mcp-sidecar/save-fact-server.py
  (server listens on stdio, Kiro launches it as a subprocess)
"""
import json
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

ES_URL = os.environ["ELASTICSEARCH_URL"]
ES_API_KEY = os.environ["ELASTICSEARCH_API_KEY"]
INDEX = "knowledge-facts"

es = Elasticsearch(ES_URL, api_key=ES_API_KEY)

TOOLS = [
    {
        "name": "save-knowledge-fact",
        "description": "Save a new architectural decision or technical fact to long-term memory. Use when the user confirms a technology choice, documents a decision, or wants to remember something important about the project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fact": {
                    "type": "string",
                    "description": "The architectural decision or fact to save, as a complete sentence including rationale.",
                },
                "category": {
                    "type": "string",
                    "description": "Category: infrastructure, auth, database, payments, observability, or other.",
                },
                "project": {
                    "type": "string",
                    "description": "Project name (default: checkout-service).",
                },
                "importance": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Importance level.",
                },
                "session_id": {
                    "type": "string",
                    "description": "Session identifier (optional, defaults to agent-write).",
                },
            },
            "required": ["fact"],
        },
    }
]


def handle_save(args):
    doc = {
        "session_id": args.get("session_id", "agent-write"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": args.get("category", "general"),
        "fact": args["fact"],
        "project": args.get("project", "checkout-service"),
        "importance": args.get("importance", "medium"),
    }
    result = es.index(index=INDEX, document=doc, refresh="wait_for")
    doc_id = result["_id"]
    return {"saved": True, "id": doc_id, "fact": doc["fact"]}


def read_message():
    line = sys.stdin.readline()
    if not line:
        return None
    header = line.strip()
    if not header.startswith("Content-Length:"):
        return None
    length = int(header.split(":")[1].strip())
    sys.stdin.readline()  # blank line
    body = sys.stdin.read(length)
    return json.loads(body)


def send_message(msg):
    body = json.dumps(msg)
    sys.stdout.write(f"Content-Length: {len(body)}\r\n\r\n{body}")
    sys.stdout.flush()


def main():
    while True:
        msg = read_message()
        if msg is None:
            break

        method = msg.get("method")
        msg_id = msg.get("id")

        if method == "initialize":
            send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "save-fact-sidecar", "version": "1.0.0"},
                },
            })

        elif method == "tools/list":
            send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOLS},
            })

        elif method == "tools/call":
            tool_name = msg["params"]["name"]
            tool_args = msg["params"].get("arguments", {})
            if tool_name == "save-knowledge-fact":
                try:
                    result = handle_save(tool_args)
                    send_message({
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(result)}],
                            "isError": False,
                        },
                    })
                except Exception as exc:
                    send_message({
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": f"Error: {exc}"}],
                            "isError": True,
                        },
                    })
            else:
                send_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                })

        elif method in ("notifications/initialized", "notifications/cancelled"):
            pass  # no response needed

        elif msg_id is not None:
            send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            })


if __name__ == "__main__":
    main()
