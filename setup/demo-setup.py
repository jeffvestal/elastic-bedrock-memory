"""
Demo setup, status check, and reset for elastic-bedrock-memory (AWS Summit NYC 2026).

Usage:
  python3 setup/demo-setup.py            # status check + pre-demo checklist
  python3 setup/demo-setup.py --setup    # first-time: create workflow + agent (enables write path)
  python3 setup/demo-setup.py --reset    # wipe docs + re-seed + re-create agent
  python3 setup/demo-setup.py --nuclear  # delete + recreate indices + full rebuild
  python3 setup/demo-setup.py --prep     # remove elastic-memory from mcp.json (pre-recording state)
  python3 setup/demo-setup.py --add-mcp  # restore elastic-memory to mcp.json (post-Scene-3 state)
"""
import argparse
import base64
import importlib.util
import json
import os
import subprocess
import sys

import requests
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ES_URL = os.environ["ELASTICSEARCH_URL"]
ES_API_KEY = os.environ["ELASTICSEARCH_API_KEY"]
KIBANA_URL = os.environ["KIBANA_URL"].rstrip("/")

MCP_JSON = os.path.expanduser("~/.kiro/settings/mcp.json")
MCP_SERVER_NAME = "elastic-memory"

def _mcp_server_config():
    user = os.environ.get("KIBANA_USER", "")
    password = os.environ.get("KIBANA_PASSWORD", "")
    basic_b64 = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {
        "url": f"{os.environ.get('KIBANA_URL', '').rstrip('/')}/api/agent_builder/mcp",
        "headers": {
            "Authorization": f"Basic {basic_b64}",
            "kbn-xsrf": "true",
            "Accept": "application/json",
        }
    }

CHECKOUT_DEMO_DIR = os.path.expanduser("~/repos/checkout-service-demo")
CHECKOUT_DEMO_README = os.path.join(CHECKOUT_DEMO_DIR, "README.md")
CHECKOUT_DEMO_README_CONTENT = "# checkout-service\n\nE-commerce checkout service.\n"

AGENT_ID = "checkout-service-memory"
TOOL_IDS = [
    "search-conversation-history",
    "search-knowledge-facts",
    "get-recent-conversations",
    "list-sessions",
    "save-knowledge-fact",
]
EXPECTED_DOCS = {
    "conversation-history": 40,
    "knowledge-facts": 18,
    "session-metadata": 10,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def es_client():
    return Elasticsearch(ES_URL, api_key=ES_API_KEY)


def kibana_session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json", "kbn-xsrf": "true", "Accept": "application/json"})
    if os.environ.get("KIBANA_USER") and os.environ.get("KIBANA_PASSWORD"):
        s.auth = (os.environ["KIBANA_USER"], os.environ["KIBANA_PASSWORD"])
    elif os.environ.get("KIBANA_API_KEY"):
        s.headers["Authorization"] = f"ApiKey {os.environ['KIBANA_API_KEY']}"
    else:
        raise ValueError("Set KIBANA_USER+KIBANA_PASSWORD or KIBANA_API_KEY in .env")
    return s


def load_script(rel_path):
    """Import a sibling script by file path (handles hyphenated names)."""
    abs_path = os.path.join(BASE_DIR, rel_path)
    spec = importlib.util.spec_from_file_location("_demo_mod", abs_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# mcp.json management
# ---------------------------------------------------------------------------

def read_mcp_json():
    if not os.path.exists(MCP_JSON):
        return {"mcpServers": {}}
    with open(MCP_JSON) as f:
        return json.load(f)


def write_mcp_json(data):
    with open(MCP_JSON, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def mcp_has_elastic():
    return MCP_SERVER_NAME in read_mcp_json().get("mcpServers", {})


def ensure_checkout_demo_dir():
    os.makedirs(CHECKOUT_DEMO_DIR, exist_ok=True)
    with open(CHECKOUT_DEMO_README, "w") as f:
        f.write(CHECKOUT_DEMO_README_CONTENT)
    print(f"  checkout-service-demo README reset: {CHECKOUT_DEMO_README}")


def mcp_remove_elastic():
    data = read_mcp_json()
    if MCP_SERVER_NAME in data.get("mcpServers", {}):
        del data["mcpServers"][MCP_SERVER_NAME]
        write_mcp_json(data)
        print(f"  Removed '{MCP_SERVER_NAME}' from {MCP_JSON}")
        print("  ⚠️  Restart Kiro for this to take effect.")
    else:
        print(f"  '{MCP_SERVER_NAME}' was not in {MCP_JSON} — nothing to remove.")


def mcp_add_elastic():
    data = read_mcp_json()
    data.setdefault("mcpServers", {})[MCP_SERVER_NAME] = _mcp_server_config()
    write_mcp_json(data)
    print(f"  Added '{MCP_SERVER_NAME}' to {MCP_JSON}")
    print("  ⚠️  Restart Kiro for this to take effect.")


# ---------------------------------------------------------------------------
# Status check
# ---------------------------------------------------------------------------

def check_status():
    all_ok = True
    print("\n=== elastic-bedrock-memory Demo Status ===\n")

    # mcp.json state (recording pre-condition)
    if mcp_has_elastic():
        print(f"  mcp.json:    ⚠️  elastic-memory IS present — run --prep to remove before recording Scenes 2-3")
    else:
        print(f"  mcp.json:    ✅  elastic-memory not present (correct for pre-recording)")
    print()

    # ES connectivity (serverless-safe — no cluster health API)
    try:
        es = es_client()
        info = es.info()
        version = info.get("version", {}).get("number", "unknown")
        print(f"  ES cluster:  ✅  connected (v{version})")
    except Exception as exc:
        print(f"  ES cluster:  ❌  {exc}")
        print("\nCannot reach Elasticsearch — aborting remaining checks.")
        return False

    # Index doc counts
    print()
    for index, expected in EXPECTED_DOCS.items():
        try:
            count = es.count(index=index)["count"]
            if count == expected:
                mark = "✅"
            elif count == 0:
                mark = "❌  EMPTY"
                all_ok = False
            else:
                mark = f"⚠️   {count} docs (expected {expected}) — run --reset to restore"
                all_ok = False
            if count == expected:
                print(f"  {index:<30} {mark}  ({count} docs)")
            else:
                print(f"  {index:<30} {mark}")
        except Exception as exc:
            print(f"  {index:<30} ❌  {exc}")
            all_ok = False

    # Kibana connectivity
    print()
    try:
        kib = kibana_session()
        resp = kib.get(f"{KIBANA_URL}/api/status", timeout=10)
        if resp.status_code == 200:
            print(f"  Kibana:      ✅  connected")
        else:
            print(f"  Kibana:      ❌  HTTP {resp.status_code}")
            all_ok = False
    except Exception as exc:
        print(f"  Kibana:      ❌  {exc}")
        return False

    # Agent exists
    resp = kib.get(f"{KIBANA_URL}/api/agent_builder/agents/{AGENT_ID}", timeout=10)
    if resp.status_code == 200:
        print(f"  Agent:       ✅  {AGENT_ID}")
    else:
        print(f"  Agent:       ❌  {AGENT_ID} not found (HTTP {resp.status_code})")
        all_ok = False

    # Tools (save-knowledge-fact is soft-required: warn if missing, only fail if read tools are missing)
    READ_TOOL_IDS = [t for t in TOOL_IDS if t != "save-knowledge-fact"]
    missing_read = [t for t in READ_TOOL_IDS
                    if kib.get(f"{KIBANA_URL}/api/agent_builder/tools/{t}", timeout=10).status_code != 200]
    write_tool_resp = kib.get(f"{KIBANA_URL}/api/agent_builder/tools/save-knowledge-fact", timeout=10)
    write_tool_ok = write_tool_resp.status_code == 200

    if not missing_read and write_tool_ok:
        print(f"  Tools:       ✅  {len(TOOL_IDS)}/{len(TOOL_IDS)} (read + write)")
    elif not missing_read and not write_tool_ok:
        print(f"  Tools:       ⚠️   {len(READ_TOOL_IDS)}/{len(TOOL_IDS)} — save-knowledge-fact missing (write path not ready)")
        print(f"               Run: python setup/validate-write-path.py && python setup/create-agent.py")
        all_ok = False
    else:
        print(f"  Tools:       ❌  missing read tools: {', '.join(missing_read)}")
        all_ok = False

    print()
    if all_ok:
        print("  ✅  All checks passed — demo is ready.\n")
    else:
        print("  ⚠️   Some checks failed. Run:  python setup/demo-setup.py --reset\n")

    return all_ok


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------

def wipe_docs(es):
    print("  Wiping docs from indices...")
    for index in EXPECTED_DOCS:
        result = es.delete_by_query(
            index=index,
            body={"query": {"match_all": {}}},
            wait_for_completion=True,
            refresh=True,
        )
        print(f"    {index}: {result.get('deleted', 0)} docs deleted")


def recreate_indices(es):
    print("  Deleting + recreating indices...")
    indices_mod = load_script("setup/create-indices.py")
    for name in indices_mod.INDICES:
        if es.indices.exists(index=name):
            es.indices.delete(index=name)
            print(f"    Deleted: {name}")
    indices_mod.create_indices()


def reseed(es):
    print("  Seeding demo data...")
    seed_mod = load_script("demo-data/seed.py")
    convs, facts, sessions = seed_mod.build_docs()
    all_docs = convs + facts + sessions
    successes, errors = helpers.bulk(es, all_docs, raise_on_error=False)
    print(f"    Indexed {successes} docs")
    if errors:
        print(f"    Errors: {errors}")


def recreate_agent():
    print("  Re-creating agent + skill + tools...")
    agent_mod = load_script("setup/create-agent.py")
    agent_mod.upsert_skill(agent_mod.SKILL)
    all_tools = agent_mod.TOOLS + ([agent_mod.WRITE_TOOL] if agent_mod.WRITE_TOOL else [])
    for tool in all_tools:
        agent_mod.upsert_tool(tool)
    agent_mod.upsert_agent(agent_mod.AGENT)


def run_setup():
    """First-time setup: create workflow (write path) + create agent."""
    print("\n=== First-Time Setup: Write Path + Agent ===\n")
    scripts_dir = os.path.join(BASE_DIR, "setup")

    print("Step 1/2 — Workflow + Jina inference validation...")
    result = subprocess.run(
        ["python3", os.path.join(scripts_dir, "validate-write-path.py")],
        env={**os.environ},
    )
    if result.returncode not in (0, 4):  # 4 = execute endpoint not found (non-fatal)
        print(f"\n  ❌  validate-write-path.py exited {result.returncode} — fix above errors before continuing.")
        sys.exit(result.returncode)

    # Reload .env so WORKFLOW_ID written by validate-write-path.py is in os.environ
    load_dotenv(override=True)

    print("\nStep 2/2 — Agent Builder agent + tools...")
    result = subprocess.run(
        ["python3", os.path.join(scripts_dir, "create-agent.py")],
        env={**os.environ},
    )
    if result.returncode != 0:
        print(f"\n  ❌  create-agent.py exited {result.returncode}")
        sys.exit(result.returncode)

    print("\n  ✅  Setup complete. Run:  python3 setup/demo-setup.py  to verify status.\n")


def reset(nuclear=False):
    print("\n=== Resetting Demo State ===\n")
    es = es_client()

    if nuclear:
        recreate_indices(es)
    else:
        wipe_docs(es)

    print()
    reseed(es)
    print()
    recreate_agent()
    print("\n  Reset complete.\n")


# ---------------------------------------------------------------------------
# Pre-demo checklist
# ---------------------------------------------------------------------------

def print_checklist():
    print("=== Pre-Demo Checklist (manual steps) ===\n")
    print("  Before recording:")
    print("    [ ] Re-seed within 2 weeks of recording:  python3 setup/demo-setup.py --reset")
    print("    [ ] ~/.kiro/agents/checkout-memory.json installed (copy from kiro-config/)")
    print("    [ ] Kiro chat panel cleared")
    print(f"    [ ] Browser open to {KIBANA_URL}/app/agent_builder")
    print("    [ ] Font 16px+ in both Kiro and Kibana")
    print("    [ ] Window 1920×1080, menubar/dock hidden")
    print("    [ ] Test Scene 5 Q4 write beat: save CDN decision, start new session, confirm read-back")
    print()
    print("  Scene 2-3 (within-session + stateless failure):")
    print("    [ ] Run --prep first (removes elastic-memory, resets checkout-service-demo README)")
    print("    [ ] Launch Kiro from ~/repos/checkout-service-demo/ — NOT elastic-bedrock-memory")
    print("    [ ] Restart Kiro after --prep")
    print()
    print("  Scene 4+ (wire the memory + main demo):")
    print("    [ ] Run --add-mcp (restores elastic-memory to mcp.json)")
    print("    [ ] Restart Kiro")
    print("    [ ] In Kiro: type /agent → select checkout-memory")
    print("    [ ] Confirm elastic-memory shows 5 tools (/mcp list — should include save-knowledge-fact)")
    print()
    print("  Commands:")
    print("    python3 setup/demo-setup.py --setup    # first-time: create workflow + agent (enables write path)")
    print("    python3 setup/demo-setup.py --prep     # remove elastic-memory from mcp.json (before Scenes 2-3)")
    print("    python3 setup/demo-setup.py --add-mcp  # restore elastic-memory to mcp.json (before Scene 4)")
    print("    python3 setup/demo-setup.py --reset    # wipe docs + re-seed + re-create agent")
    print("    python3 setup/demo-setup.py --nuclear  # delete + recreate indices + full rebuild")
    print()


def clean():
    """Empty Elastic so the live-build segment (Segment 3) shows real creation on
    camera: delete the 3 indices + the agent, tools, and skill. Leaves the
    save-knowledge-fact workflow intact (create-agent reuses WORKFLOW_ID)."""
    print("\n=== Clean: empty Elastic for the live-build capture ===\n")
    es = es_client()
    for name in EXPECTED_DOCS:
        if es.indices.exists(index=name):
            es.indices.delete(index=name)
            print(f"  index deleted: {name}")
        else:
            print(f"  index absent:  {name}")
    kb = kibana_session()
    base = os.environ["KIBANA_URL"].rstrip("/")

    def _del(path, label):
        try:
            r = kb.delete(f"{base}/api/agent_builder/{path}")
            status = "deleted" if r.status_code in (200, 204) else f"{r.status_code} (skip)"
            print(f"  {status}: {label}")
        except Exception as e:
            print(f"  error deleting {label}: {e}")

    _del(f"agents/{AGENT_ID}", f"agent {AGENT_ID}")
    for tid in TOOL_IDS:
        _del(f"tools/{tid}", f"tool {tid}")
    _del("skills/checkout-memory-retrieval", "skill checkout-memory-retrieval")
    print("\n  Elastic is empty. Now record Segment 3 on camera:")
    print("    python3 setup/create-indices.py   # shows indices CREATED (semantic_text)")
    print("    python3 setup/create-agent.py      # shows agent + 5 tools created")
    print("    python3 demo-data/seed.py          # loads 67 docs")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo setup + status check")
    parser.add_argument("--setup", action="store_true", help="First-time: create workflow + agent (enables write path)")
    parser.add_argument("--reset", action="store_true", help="Wipe docs + re-seed + re-create agent")
    parser.add_argument("--nuclear", action="store_true", help="Delete + recreate indices + full rebuild")
    parser.add_argument("--prep", action="store_true", help="Remove elastic-memory from mcp.json (pre-recording state for Scenes 2-3)")
    parser.add_argument("--add-mcp", action="store_true", help="Add elastic-memory to mcp.json (post-Scene-3 state)")
    parser.add_argument("--clean", action="store_true", help="Empty Elastic (delete indices + agent/tools/skill) for the live-build capture; keeps the workflow")
    args = parser.parse_args()

    if args.setup:
        run_setup()
    if args.clean:
        clean()
    if args.reset or args.nuclear:
        reset(nuclear=args.nuclear)
    if args.prep:
        print("\n=== Prep: pre-recording state (Act 1 / amnesia) ===\n")
        mcp_remove_elastic()
        print("  Reset the checkout-service-demo codebase to baseline:")
        print(f"    git -C {CHECKOUT_DEMO_DIR} checkout .")
        print()
    if args.add_mcp:
        print("\n=== Adding elastic-memory to mcp.json ===\n")
        mcp_add_elastic()
        print()

    ok = check_status()
    print_checklist()
    sys.exit(0 if ok else 1)
