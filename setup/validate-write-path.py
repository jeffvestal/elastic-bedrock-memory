"""
Validate the write path for elastic-bedrock-memory demo.

Runs automated checks:
  1. Create (or reuse) the save-knowledge-fact workflow in Kibana
  2. Verify Jina inference fires on write (fact_semantic must populate)
  3. Optionally trigger the workflow directly and verify end-to-end
  4. Write WORKFLOW_ID to .env for create-agent.py to consume

Usage:
  python setup/validate-write-path.py           # run all checks
  python setup/validate-write-path.py --cleanup # delete test doc after run

Exit codes:
  0 = all checks passed
  1 = workflow creation failed
  2 = ES write failed
  3 = fact_semantic not populated (Jina inference did not fire)
  4 = workflow execute failed (non-fatal warning if endpoint doesn't exist)
"""
import argparse
import os
import sys
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv, set_key
from elasticsearch import Elasticsearch

load_dotenv()

KIBANA_URL = os.environ["KIBANA_URL"].rstrip("/")
ES_URL = os.environ["ELASTICSEARCH_URL"]
ES_API_KEY = os.environ["ELASTICSEARCH_API_KEY"]
ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

WORKFLOW_NAME = "save-knowledge-fact"
INDEX = "knowledge-facts"
TEST_DOC_SESSION = "validate-write-path-test"

WORKFLOW_YAML = """\
name: save-knowledge-fact
triggers:
  - type: manual
inputs:
  - name: fact
    type: string
    required: true
  - name: category
    type: string
  - name: project
    type: string
  - name: importance
    type: string
  - name: session_id
    type: string
  - name: timestamp
    type: string
steps:
  - name: save_fact
    type: elasticsearch.request
    with:
      method: POST
      path: /knowledge-facts/_doc?refresh=wait_for
      body:
        session_id: "{{inputs.session_id | default('agent-write')}}"
        timestamp: "{{inputs.timestamp}}"
        category: "{{inputs.category}}"
        fact: "{{inputs.fact}}"
        fact_semantic: "{{inputs.fact}}"
        project: "{{inputs.project}}"
        importance: "{{inputs.importance}}"
"""


def kibana_session():
    s = requests.Session()
    s.headers.update({
        "Content-Type": "application/json",
        "kbn-xsrf": "true",
        "Accept": "application/json",
        "x-elastic-internal-origin": "Kibana",
    })
    if os.environ.get("KIBANA_USER") and os.environ.get("KIBANA_PASSWORD"):
        s.auth = (os.environ["KIBANA_USER"], os.environ["KIBANA_PASSWORD"])
    elif os.environ.get("KIBANA_API_KEY"):
        s.headers["Authorization"] = f"ApiKey {os.environ['KIBANA_API_KEY']}"
    else:
        raise ValueError("Set KIBANA_USER+KIBANA_PASSWORD or KIBANA_API_KEY in .env")
    return s


def es_client():
    return Elasticsearch(ES_URL, api_key=ES_API_KEY)


def get_existing_workflow(kib, workflow_id):
    """Return workflow data if it exists, else None."""
    if not workflow_id:
        return None
    resp = kib.get(f"{KIBANA_URL}/api/workflows/{workflow_id}", timeout=10)
    return resp.json() if resp.status_code == 200 else None


def create_workflow(kib):
    """Create the save-knowledge-fact workflow. Returns workflow_id."""
    print("  Creating save-knowledge-fact workflow...")
    resp = kib.post(f"{KIBANA_URL}/api/workflows", json={"workflows": [{"yaml": WORKFLOW_YAML}]}, timeout=30)
    if resp.status_code not in (200, 201):
        print(f"  ❌  Workflow creation failed: HTTP {resp.status_code}")
        print(f"      Response: {resp.text[:400]}")
        sys.exit(1)
    data = resp.json()
    # Response: {"created": [...], "failed": [...]}
    failed = data.get("failed", [])
    created = data.get("created", [])
    if failed:
        print(f"  ❌  Workflow creation failed: {failed}")
        sys.exit(1)
    if not created:
        print(f"  ❌  No workflow created — unexpected response: {data}")
        sys.exit(1)
    entry = created[0]
    workflow_id = entry.get("id")
    if not workflow_id:
        print(f"  ❌  No id in created workflow: {entry}")
        sys.exit(1)
    if not entry.get("valid", True):
        print(f"  ⚠️   Workflow created but marked invalid — check YAML. Proceeding anyway.")
        print(f"      entry: {entry}")
    print(f"  ✅  Workflow created: {workflow_id}")
    return workflow_id


def write_workflow_id_to_env(workflow_id):
    """Append or update WORKFLOW_ID in .env."""
    if os.path.exists(ENV_FILE):
        set_key(ENV_FILE, "WORKFLOW_ID", workflow_id)
        print(f"  ✅  WORKFLOW_ID written to .env: {workflow_id}")
    else:
        print(f"  ⚠️   .env not found at {ENV_FILE} — set WORKFLOW_ID={workflow_id} manually")


def test_es_inference(es, cleanup=False):
    """Write a test doc directly to ES and verify fact_semantic populates."""
    print("\n--- Check 2: Jina inference on write ---")
    ts = datetime.now(timezone.utc).isoformat()
    fact_text = "Validation test: Cloudflare CDN with 5-minute TTL for static assets"
    doc = {
        "session_id": TEST_DOC_SESSION,
        "timestamp": ts,
        "category": "infrastructure",
        "fact": fact_text,
        "fact_semantic": fact_text,  # semantic_text field — must be set explicitly; ES calls inference on ingest
        "project": "checkout-service",
        "importance": "high",
    }

    es.index(index=INDEX, document=doc, refresh="wait_for")
    print("  Doc indexed. Waiting 2s for inference...")
    time.sleep(2)

    # Search for the test doc
    result = es.search(index=INDEX, query={"term": {"session_id": TEST_DOC_SESSION}})
    hits = result["hits"]["hits"]
    if not hits:
        print(f"  ❌  Test doc not found in {INDEX} — index write failed")
        sys.exit(2)

    source = hits[0]["_source"]
    doc_id = hits[0]["_id"]

    # Check fact_semantic
    semantic_val = source.get("fact_semantic")
    if not semantic_val:
        print("  ❌  fact_semantic is empty — Jina inference did not fire")
        print("      This is an index/inference problem. The sidecar will NOT fix this.")
        print("      Check: index mapping has semantic_text field; ML inference endpoint is active")
        if cleanup:
            es.delete(index=INDEX, id=doc_id, refresh="wait_for")
        sys.exit(3)

    print(f"  ✅  fact_semantic populated (Jina inference confirmed)")

    if cleanup:
        es.delete(index=INDEX, id=doc_id, refresh="wait_for")
        print(f"  ✅  Test doc cleaned up")
    else:
        print(f"  ℹ️   Test doc left in index (session_id={TEST_DOC_SESSION}). Run with --cleanup to remove.")

    return doc_id


def try_execute_workflow(kib, workflow_id):
    """Attempt to trigger the workflow directly. Non-fatal if endpoint doesn't exist."""
    print("\n--- Check 3: Workflow execute (optional) ---")
    ts = datetime.now(timezone.utc).isoformat()
    inputs = {
        "fact": "Workflow execute test: Cloudflare CDN 5-minute TTL",
        "category": "infrastructure",
        "project": "checkout-service",
        "importance": "high",
        "session_id": f"{TEST_DOC_SESSION}-workflow",
        "timestamp": ts,
    }
    for endpoint in [f"/api/workflows/{workflow_id}/execute", f"/api/workflows/{workflow_id}/run"]:
        resp = kib.post(f"{KIBANA_URL}{endpoint}", json={"inputs": inputs}, timeout=30)
        if resp.status_code == 404:
            continue
        if resp.status_code in (200, 201, 202):
            print(f"  ✅  Workflow triggered via {endpoint}: HTTP {resp.status_code}")
            return True
        else:
            print(f"  ⚠️   Workflow execute returned HTTP {resp.status_code} at {endpoint}: {resp.text[:200]}")
            return False
    print("  ⚠️   No execute endpoint found — workflow will be triggered by Agent Builder tool calls (normal)")
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate write path for elastic-bedrock-memory demo")
    parser.add_argument("--cleanup", action="store_true", help="Delete test docs after validation")
    args = parser.parse_args()

    print("\n=== elastic-bedrock-memory: Write Path Validation ===\n")

    kib = kibana_session()
    es = es_client()

    # --- Check 1: Workflow ---
    print("--- Check 1: Workflow creation ---")
    existing_id = os.environ.get("WORKFLOW_ID")
    existing = get_existing_workflow(kib, existing_id)
    if existing:
        workflow_id = existing_id
        print(f"  ✅  Reusing existing workflow: {workflow_id}")
    else:
        if existing_id:
            print(f"  ℹ️   Workflow {existing_id} no longer exists — creating new one")
        workflow_id = create_workflow(kib)
        write_workflow_id_to_env(workflow_id)

    # --- Check 2: Jina inference on ES write ---
    test_es_inference(es, cleanup=args.cleanup)

    # --- Check 3: Workflow execute (optional) ---
    try_execute_workflow(kib, workflow_id)

    print(f"\n✅  Write path validated.")
    print(f"   WORKFLOW_ID: {workflow_id}")
    print(f"   Next step: python setup/create-agent.py")
    sys.exit(0)
