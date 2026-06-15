# Kibana ES|QL — Demo Reference

Open this in a second tab. Copy-paste into Kibana Dev Console during Segment 6.

---

## Refund policy fact (sess-004) — what Act 2 retrieved

```esql
FROM knowledge-facts
| WHERE session_id == "sess-004"
| KEEP fact, category, importance, session_id
```

---

## Idempotency key fact (sess-007) — what Act 3 retrieved

```esql
FROM knowledge-facts
| WHERE session_id == "sess-007"
| KEEP fact, category, importance, session_id
```

---

## All facts — show the full knowledge base

```esql
FROM knowledge-facts
| KEEP fact, category, importance, session_id
| SORT session_id ASC
```
