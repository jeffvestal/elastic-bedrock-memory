"""
Seed synthetic developer memory data for the AWS Summit demo.
Scenario: Building an e-commerce checkout service over 2 weeks.

Simulates 10 past Kiro/Bedrock sessions with realistic developer conversations,
architectural decisions, bug fixes, and requirements.
"""
import os
import uuid
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv

load_dotenv()

ES_URL = os.environ["ELASTICSEARCH_URL"]
ES_API_KEY = os.environ["ELASTICSEARCH_API_KEY"]
es = Elasticsearch(ES_URL, api_key=ES_API_KEY)

PROJECT = "checkout-service"
BASE_DATE = datetime.utcnow() - timedelta(days=14)


def d(days_ago, hour=10):
    return (BASE_DATE + timedelta(days=days_ago, hours=hour)).isoformat() + "Z"


SESSIONS = [
    {
        "id": "sess-001",
        "day": 0,
        "summary": "Project kickoff — chose tech stack and database",
        "topics": ["database", "architecture", "stack-decision"],
        "exchanges": [
            ("user", "We need to build a checkout service. Should we use a relational database or a NoSQL store?",
             ["database", "architecture"]),
            ("assistant",
             "For a checkout service, PostgreSQL is the right fit: ACID transactions ensure payment integrity, relational JOINs handle order history and reporting cleanly, and Aurora Serverless v2 auto-scales to match your traffic patterns without manual capacity management. Decision recorded.",
             ["database", "architecture"]),
            ("user", "Agreed. What ORM should we use?",
             ["orm", "stack-decision"]),
            ("assistant",
             "SQLAlchemy with async support (asyncpg driver). It pairs well with FastAPI and gives you both the ORM convenience and raw SQL escape hatch for complex reporting queries.",
             ["orm", "stack-decision"]),
        ],
        "facts": [
            ("architecture", "Database: Aurora PostgreSQL (Serverless v2) — checkout requires ACID transactions for payment integrity, relational JOINs for order history and reporting. Aurora Serverless v2 handles traffic spikes without manual capacity management.", "critical"),
            ("architecture", "ORM: SQLAlchemy with asyncpg driver — async-first for FastAPI compatibility", "high"),
        ]
    },
    {
        "id": "sess-002",
        "day": 1,
        "summary": "Auth design — SSO and JWT strategy",
        "topics": ["auth", "security", "jwt"],
        "exchanges": [
            ("user", "Auth requirements: must support SSO via Okta, and we have mobile apps too.",
             ["auth", "security"]),
            ("assistant",
             "For Okta SSO + mobile: use OAuth2 with PKCE for mobile (no client secret), OIDC for web SSO. Issue short-lived JWTs (15 min) with refresh tokens stored in httpOnly cookies for web, secure storage for mobile. Token validation via Okta JWKS endpoint — don't roll your own JWT validation.",
             ["auth", "security", "jwt"]),
            ("user", "Should we use opaque tokens or JWTs?",
             ["auth", "jwt"]),
            ("assistant",
             "JWTs for your case — you need stateless validation at the API gateway level before hitting the checkout service. Opaque tokens require a token introspection call on every request which adds latency. JWTs let the gateway validate locally. Keep them short-lived (15 min) to limit exposure window.",
             ["auth", "jwt"]),
        ],
        "facts": [
            ("security", "Auth: JWT (15 min expiry) + refresh tokens. SSO via Okta OIDC. Mobile uses OAuth2 PKCE. JWTs validated at API gateway level — not opaque tokens.", "critical"),
            ("security", "JWT validation: use Okta JWKS endpoint, never roll custom validation", "critical"),
        ]
    },
    {
        "id": "sess-003",
        "day": 2,
        "summary": "API design — REST vs GraphQL decision",
        "topics": ["api-design", "graphql", "rest"],
        "exchanges": [
            ("user", "Should we use REST or GraphQL for the checkout API? Mobile team is asking.",
             ["api-design"]),
            ("assistant",
             "REST for checkout. GraphQL adds complexity (N+1 queries, caching harder) that doesn't pay off for a checkout flow which has predictable, well-defined operations: create cart, add item, apply coupon, checkout, confirm. REST endpoints map cleanly. GraphQL is better for flexible data fetching across many entity types — that's not this use case.",
             ["api-design", "rest"]),
            ("user", "Mobile team wants flexible field selection to reduce payload size.",
             ["api-design", "mobile"]),
            ("assistant",
             "Use sparse fieldsets (JSON:API style) — add a ?fields=id,total,status query param to REST endpoints. Gives mobile the payload control they want without GraphQL overhead. Much simpler to implement and cache.",
             ["api-design", "rest", "mobile"]),
        ],
        "facts": [
            ("architecture", "API: REST (not GraphQL) — checkout has predictable operations, REST maps cleanly. Mobile payload control via sparse fieldsets (?fields= param).", "high"),
        ]
    },
    {
        "id": "sess-004",
        "day": 4,
        "summary": "Payment processor integration — Stripe vs Braintree",
        "topics": ["payments", "stripe", "integration"],
        "exchanges": [
            ("user", "We need to integrate a payment processor. Stripe or Braintree?",
             ["payments"]),
            ("assistant",
             "Stripe. Better developer experience, webhooks are more reliable, Stripe Elements handles PCI scope reduction out of the box. Braintree requires more custom work for the same result. Use Stripe Payment Intents API — it handles 3DS2 authentication automatically which you'll need for EU customers.",
             ["payments", "stripe"]),
            ("user", "How do we handle webhook idempotency?",
             ["payments", "webhooks"]),
            ("assistant",
             "Store processed Stripe event IDs in a webhook_events table with a unique constraint on stripe_event_id. On receipt: check if already processed → skip. Process → insert event ID. This is your idempotency key. Stripe retries failed webhooks with the same event ID, so this pattern handles retries cleanly.",
             ["payments", "webhooks", "idempotency"]),
        ],
        "facts": [
            ("architecture", "Payment processor: Stripe (not Braintree) — better webhooks, Stripe Elements for PCI scope, Payment Intents for 3DS2/EU compliance", "critical"),
            ("engineering", "Webhook idempotency: webhook_events table with unique constraint on stripe_event_id", "high"),
        ]
    },
    {
        "id": "sess-005",
        "day": 5,
        "summary": "Bug fix — cart total calculation off by 1 cent",
        "topics": ["bug", "pricing", "floating-point"],
        "exchanges": [
            ("user", "Huge bug: cart totals are off by 1 cent on some orders. Happening with certain discount combinations.",
             ["bug", "pricing"]),
            ("assistant",
             "Classic floating point issue. You're using float arithmetic for money. Example: 19.99 - 5.00 = 14.989999999999998 in float. Fix: store all prices as integers (cents) in the database. Never use float for currency. Convert to display format only at the UI layer. This also applies to your discount and tax calculations.",
             ["bug", "pricing", "floating-point"]),
            ("user", "Do we need to migrate existing data?",
             ["bug", "migration"]),
            ("assistant",
             "Yes. Write a migration that multiplies all price columns by 100 and changes column types from DECIMAL/FLOAT to INTEGER. Update the ORM models. The migration must be run in a transaction — all columns or none. Test with the specific discount combinations that triggered the bug before deploying.",
             ["bug", "migration", "pricing"]),
        ],
        "facts": [
            ("engineering", "BUG FIX: All monetary values stored as integers (cents) in DB — float caused 1-cent rounding errors. UI layer converts to display. Migration: multiply existing values by 100, change column types to INTEGER.", "critical"),
        ]
    },
    {
        "id": "sess-006",
        "day": 7,
        "summary": "Caching strategy — Redis setup",
        "topics": ["caching", "redis", "performance"],
        "exchanges": [
            ("user", "We need caching. Product catalog is slow to load for cart.",
             ["caching", "performance"]),
            ("assistant",
             "Redis for two things: (1) product catalog cache with 5-minute TTL — cache at product ID granularity, not full catalog. (2) cart session state — store cart in Redis with 24h TTL, write-through to PostgreSQL on checkout. Use ElastiCache Redis Serverless to match your Aurora Serverless scaling model.",
             ["caching", "redis"]),
            ("user", "What's the cache invalidation strategy for product updates?",
             ["caching", "invalidation"]),
            ("assistant",
             "Event-driven invalidation: when a product is updated in the catalog service, it publishes a ProductUpdated event to EventBridge. The checkout service subscribes and deletes the specific Redis key (product:{id}). Don't use TTL-only invalidation — stale prices in cart are a critical issue.",
             ["caching", "invalidation", "eventbridge"]),
        ],
        "facts": [
            ("architecture", "Caching: Redis (ElastiCache Serverless) — product catalog (5min TTL, per-product key), cart session (24h, write-through to PG on checkout)", "high"),
            ("architecture", "Cache invalidation: event-driven via EventBridge ProductUpdated event → delete Redis key. TTL-only insufficient for pricing data.", "high"),
        ]
    },
    {
        "id": "sess-007",
        "day": 8,
        "summary": "Error handling and retry strategy",
        "topics": ["error-handling", "retry", "resilience"],
        "exchanges": [
            ("user", "How should we handle Stripe API timeouts and retries?",
             ["error-handling", "stripe", "retry"]),
            ("assistant",
             "Exponential backoff with jitter for Stripe retries: initial delay 1s, max 3 retries, max delay 8s, add ±20% jitter to avoid thundering herd. Never retry charge creation without idempotency key — use Stripe's idempotency key header (your internal order ID works). Idempotency key ensures Stripe won't double-charge on retry.",
             ["error-handling", "retry", "stripe"]),
            ("user", "What about database connection failures during high load?",
             ["error-handling", "database", "resilience"]),
            ("assistant",
             "Connection pool with circuit breaker: SQLAlchemy pool_size=10, max_overflow=20. Add a circuit breaker (use the circuitbreaker library) that opens after 5 consecutive DB failures and half-opens after 30s. During open state, return 503 immediately — fail fast rather than queuing requests that will timeout anyway.",
             ["error-handling", "database", "circuit-breaker"]),
        ],
        "facts": [
            ("engineering", "Stripe retry: exponential backoff, max 3 retries, jitter ±20%, always use idempotency key (order ID). Never retry charge creation without idempotency key.", "critical"),
            ("engineering", "DB resilience: SQLAlchemy pool_size=10, max_overflow=20 + circuit breaker (5 failures → open, 30s half-open)", "high"),
        ]
    },
    {
        "id": "sess-008",
        "day": 10,
        "summary": "Performance testing results — identified N+1 query problem",
        "topics": ["performance", "sql", "n+1"],
        "exchanges": [
            ("user", "Load testing is showing cart load at 800ms P99. That's too slow. Running k6 against the cart endpoint.",
             ["performance", "load-testing"]),
            ("assistant",
             "800ms P99 is an N+1 query signature. Add SQLAlchemy query logging in staging and look for repeated queries with only the ID changing. My bet: loading cart items is fetching each product in a separate query. Fix: use selectinload() or joinedload() on the cart → items → product relationship.",
             ["performance", "sql", "n+1"]),
            ("user", "You were right — 47 queries for a cart with 3 items. Fixed with joinedload. Now at 45ms P99.",
             ["performance", "sql"]),
            ("assistant",
             "45ms P99 is excellent. The 47 queries confirms the N+1: 1 for cart + 1 for items list + 1 per product (3) + joins for variants, etc. Keep an eye on carts with many items — joinedload can produce large result sets. Consider selectinload for items>10 scenario.",
             ["performance", "sql"]),
        ],
        "facts": [
            ("engineering", "Performance fix: N+1 query on cart load — SQLAlchemy joinedload() on cart→items→product. Reduced from 800ms P99 (47 queries) to 45ms P99. Consider selectinload for carts with >10 items.", "high"),
        ]
    },
    {
        "id": "sess-009",
        "day": 12,
        "summary": "Deployment — Dockerization and ECS setup",
        "topics": ["deployment", "docker", "ecs", "aws"],
        "exchanges": [
            ("user", "Ready to containerize. ECS Fargate or EKS?",
             ["deployment", "aws"]),
            ("assistant",
             "ECS Fargate for this service. EKS is overkill unless you already have Kubernetes expertise on the team and need cross-cluster features. Fargate: no node management, integrates natively with ALB, ECR, CloudWatch, IAM roles for tasks. Use a multi-stage Dockerfile: builder stage (full Python) → runtime stage (slim Python). Target image under 200MB.",
             ["deployment", "ecs", "docker"]),
            ("user", "How do we handle secrets in ECS?",
             ["deployment", "secrets", "security"]),
            ("assistant",
             "AWS Secrets Manager + ECS task definition secretsManagerArns. Never put secrets in environment variables directly or in the Docker image. IAM task role with secretsmanager:GetSecretValue on specific ARNs only. Rotate the Stripe API key and DB password in Secrets Manager — ECS picks up new values on task restart.",
             ["deployment", "secrets", "security"]),
        ],
        "facts": [
            ("architecture", "Deployment: ECS Fargate (not EKS) — simpler ops, native AWS integrations, no node management needed at current scale", "high"),
            ("security", "Secrets management: AWS Secrets Manager via ECS task definition secretsManagerArns. IAM task role scoped to specific secret ARNs. Never use env vars for secrets.", "critical"),
        ]
    },
    {
        "id": "sess-010",
        "day": 13,
        "summary": "Observability setup — structured logging and tracing",
        "topics": ["observability", "logging", "tracing", "cloudwatch"],
        "exchanges": [
            ("user", "We need observability before we go to production.",
             ["observability"]),
            ("assistant",
             "Three pillars: (1) Structured JSON logs → CloudWatch Logs via awslogs driver. Include: request_id, user_id, order_id, duration_ms on every log line. (2) X-Ray distributed tracing — add aws_xray_sdk to FastAPI middleware. (3) Custom CloudWatch metrics: cart_conversion_rate, checkout_failures_total, payment_latency_p99. Set alarms on checkout_failures>1% and payment_latency_p99>500ms.",
             ["observability", "logging", "tracing"]),
            ("user", "What correlation ID strategy?",
             ["observability", "logging"]),
            ("assistant",
             "Use X-Request-ID header: if present, use it as correlation ID; if absent, generate UUID. Propagate via contextvars through the entire request. Include in every log line and in the response header so clients can reference it in support tickets. This gives you end-to-end tracing from ALB access log through your service to Stripe webhook responses.",
             ["observability", "correlation-id"]),
        ],
        "facts": [
            ("engineering", "Observability: JSON structured logs → CloudWatch, X-Ray tracing (aws_xray_sdk), custom metrics: cart_conversion_rate, checkout_failures_total, payment_latency_p99", "high"),
            ("engineering", "Correlation ID: X-Request-ID header, propagate via contextvars, include in all logs and response headers", "high"),
        ]
    },
]


def build_docs():
    conversation_docs = []
    fact_docs = []
    session_docs = []

    for sess in SESSIONS:
        sid = sess["id"]
        day = sess["day"]

        session_docs.append({
            "_index": "session-metadata",
            "_id": sid,
            "_source": {
                "session_id": sid,
                "start_time": d(day, 9),
                "end_time": d(day, 11),
                "summary": sess["summary"],
                "project": PROJECT,
                "topics": sess["topics"],
            }
        })

        for i, (role, content, tags) in enumerate(sess["exchanges"]):
            conversation_docs.append({
                "_index": "conversation-history",
                "_id": f"{sid}-{i}",
                "_source": {
                    "session_id": sid,
                    "timestamp": d(day, 10 + i * 0.1),
                    "role": role,
                    "content": content,
                    "content_semantic": content,
                    "topic_tags": tags,
                    "project": PROJECT,
                }
            })

        for i, (category, fact, importance) in enumerate(sess.get("facts", [])):
            fact_docs.append({
                "_index": "knowledge-facts",
                "_id": f"{sid}-fact-{i}",
                "_source": {
                    "session_id": sid,
                    "timestamp": d(day, 11),
                    "category": category,
                    "fact": fact,
                    "fact_semantic": fact,
                    "project": PROJECT,
                    "importance": importance,
                }
            })

    return conversation_docs, fact_docs, session_docs


if __name__ == "__main__":
    convs, facts, sessions = build_docs()
    all_docs = convs + facts + sessions

    print(f"Seeding {len(convs)} conversation turns, {len(facts)} facts, {len(sessions)} sessions...")
    successes, errors = helpers.bulk(es, all_docs, raise_on_error=False)
    print(f"Indexed: {successes} docs")
    if errors:
        print(f"Errors: {errors}")
    print("Done. Run a test query:")
    print(f"  ES URL: {ES_URL}")
    print(f"  Index: knowledge-facts, conversation-history, session-metadata")
