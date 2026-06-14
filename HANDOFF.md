# Handoff — elastic-bedrock-memory (AWS Summit NYC 2026)

**Updated:** 2026-06-14
**Talk:** From Stateless to Stateful: Architecting Agent Memory with Elastic and Bedrock
**Event:** AWS Summit NYC, June 17, 2026 (60 min solo)
**Repo:** github.com/jeffvestal/elastic-bedrock-memory (private — make public before June 17)

> Standing facts (infra, credentials, indices, key technical decisions) live in **CLAUDE.md**.
> This file is the *current state + what's in flight*. Read CLAUDE.md first, then this.

---

## TL;DR — where things stand

1. **The demo is fully built and was live-verified end-to-end on 2026-06-11** (Act 1 amnesiac →
   live-build → wire → Act 2 memory build + write beat → Act 3 cross-session read-back). The
   `save-knowledge-fact` write path works through Kiro. Read path works. (The old "write path
   not yet tested" risk in prior handoffs is RESOLVED.)
2. **New asset (2026-06-13/14): a "fake terminal player"** under `demo_scripts/player/` that
   replays the entire hands-on portion as a scripted movie you drive with the arrow keys —
   built to **replace live Kiro / Navattic on stage** ("forget navattic, too slow, looks
   forced"). It's verified (11/11 self-tests green) but **not yet committed**.
3. **🔜 NEXT: Jeff is going to CHANGE THE DEMO.** What changes is TBD — **ask him first.** The
   single most useful thing this handoff gives you is the **sync map** below: the artifacts
   that must change together when the demo narrative changes.

---

## ⚠️ The sync map — change these together when the demo changes

The demo narrative is duplicated across several artifacts by necessity. If Jeff changes the
story (different task than "add a refund endpoint", different decisions, different acts), ALL
of these must move in lockstep or the demo desyncs:

| Artifact | Path | Holds |
|---|---|---|
| Seeded memory (facts + conversations) | `demo-data/seed.py` | The 10 sessions / 18 facts the agent retrieves. **Source of truth for what's "in memory."** |
| Reference refund impls | `demo_scripts/reference/refunds-amnesiac.py`, `refunds-correct.py` | The wrong (policy-blind) and right (policy-aware) target code. |
| The capture run-book | `demo_scripts/aws-summit-2026-demo-runbook.md` | THE source of truth for exact prompts, act flow, reset procedures. |
| Practice guide / shot sheet / FAQ | `demo_scripts/aws-summit-2026-*.md` | Stage script, (legacy) Navattic shots, FAQ segment. |
| **Player content** | `demo_scripts/player/content.py` | The scripted replay. Verbatim Act 2/3 + reconstructed Act 1/live-build/wire. |
| Slide deck | Google Slides `151FhokgExhlNBw1FuqPwyYVWVvlyKHfAJVBUiYUYUK4` | 22 slides + speaker notes (work copy; original untouched). |

**After any demo-content change:** reseed (`python3 setup/demo-setup.py --reset`), re-verify the
read/write path through Kiro, update `content.py`, run `python3 demo_scripts/player/selftest.py`,
then update the run-book + deck.

---

## The terminal player (newest, most likely thing you'll edit)

**Location:** `demo_scripts/player/` — `play.py` (engine), `content.py` (the demo as data),
`selftest.py` (11-check harness), `README.md`.

**Run:** `python3 demo_scripts/player/play.py` (works from any dir). `--list` shows all steps;
`--from-step N` jumps in; `--speed X` scales pace; `--render-all [--speed 0]` auto-plays /
headless-dumps. Right-arrow drives it; mouse-wheel = scrollback; `q`/Ctrl-C quits.

**Interaction model (Jeff's spec — keep it):** two right-presses per turn — press 1 *types* the
prompt, press 2 is *Enter* (response streams, then stops). Session exit is **its own**
right-press beat (response stops → [→] → "Session ended" → stops → [→] → next). Pace was tuned
~40% slower than the first cut (timing constants `T_CHAR/T_WORD/T_LINE/...` at top of
`play.py`); fine-tune live with `--speed` (>1 faster, <1 slower).

**Architecture invariants — DO NOT BREAK (each has a self-test):**
- **Normal screen buffer only** — no alternate screen, no curses, no `rich.Live`, no mouse
  reporting. This is what preserves native iTerm2 scrollback. (Consequence: the status line is
  rendered *inline*, not pinned — deliberate trade-off.)
- **Lone-ESC must not hang** — `decode_key` uses a `select` timeout after `\x1b`; ESC is
  unbound; accepts both `[` and `O` arrow forms.
- **Fast-forward is a DRAIN, not a finish** — a right-press mid-stream emits *all* remaining
  fragments at zero delay; it must never skip output.
- **`shutil.get_terminal_size()` per render**; left-arrow = clear (`\x1b[H\x1b[J`) + instant
  re-render; SIGINT restores termios.
- Code blocks render **plain/dim** (matches Kiro) — no `rich` dependency.

**Content model (`content.py`):** `STEPS` = flat list the player runs; `SEGMENTS` = each act
(used by selftest). Build turns with helpers `kiro_launch / kiro_turn / kiro_idle_end /
shell_cmd`; compose output from fragments `line / blank / rule / tool / toolline / write /
code / footer / banner / status / idle / sessionend` (defined in `play.py`).

**Verbatim vs reconstructed:** Act 2 + Act 3 are **verbatim** from the 2026-06-11 capture
(tool calls, cited fact IDs `sess-004-fact-2` etc., the saved fact id `Wn9ktp4B`, the diffs,
the `▸ Credits` footers). Act 1, the live-build script output, and the `/agent` picks are
**reconstructed** (marked `# RECONSTRUCTED — swap for real capture`). The `/agent` step is a
simplified one-liner, not Kiro's real picker UI.

**Verification discipline (carry this forward):** there's a 5-round verify-and-fix loop in the
plan. After any `content.py` change, run `selftest.py` (no TTY/network needed — it checks
schema, render, two-press structure, act-contrast invariants, verbatim-token fidelity, Act 1
policy-gap fidelity, key decode incl. lone-ESC, fast-forward drain, pty smoke). Section-B
human checks (color/glyph/scrollback/pacing on the **stage** iTerm2 profile) are still pending
— only Jeff can judge those.

**Plan/design doc:** `/Users/jeffvestal/.claude/plans/crystalline-wondering-parasol.md`
(full design + Opus review + verification spec + the round log).

---

## The demo narrative (what the player depicts) — current version

ONE coding task built twice: **add a refund endpoint** to a FastAPI checkout service
(`~/repos/checkout-service-demo`, **separate repo**; reset between takes with
`git -C ~/repos/checkout-service-demo checkout .`).

- **Act 1 — amnesiac (stock Kiro):** reads the repo, gets the *code patterns* right (integer
  cents, Stripe idempotency+backoff, JWT, async) but is **policy-blind** — no cumulative cap,
  no 90-day window, ships an **amount-based** idempotency key. Makes **no
  `search-knowledge-facts` call**. (That absence is the whole contrast.)
- **Live-build:** `create-indices.py` → `create-agent.py` → `seed.py` on camera.
- **Wire:** `--add-mcp`, then `/agent` → checkout-memory.
- **Act 2 — memory Kiro:** SAME prompt → calls `search-knowledge-facts` first, cites the
  sessions, builds it right (cap + 90-day window + cents + JWT). Then the **write beat**:
  fixes the idempotency key to a per-attempt UUID and saves that decision via
  `save-knowledge-fact`.
- **Act 3 — fresh session:** `/agent` → checkout-memory, asks the idempotency convention →
  reads back the just-saved UUID rule (fact `Wn9ktp4B`). Proves the write→read loop.

**Seeded decisions that make it land** (all in `seed.py`): money = integer cents (sess-005),
JWT on every route (sess-002), Stripe idempotency key (sess-004/007), Aurora PostgreSQL
(sess-001), refund policy = cumulative cap + 90-day window (sess-004), recent observability
work (sess-010). 10 sessions / 18 facts / ~40 conversation turns (68 docs total).

---

## Setup / reset commands (full detail in CLAUDE.md + run-book)

```bash
python3 setup/demo-setup.py             # status check (shows all green when healthy)
python3 setup/demo-setup.py --setup     # first-time: workflow + agent (enables write path)
python3 setup/demo-setup.py --reset     # wipe docs + reseed (clean 18 facts) + recreate agent
python3 setup/demo-setup.py --clean     # empty Elastic for the live-build capture (keeps workflow)
python3 setup/demo-setup.py --prep      # remove elastic-memory from mcp.json (Act 1 amnesia state)
python3 setup/demo-setup.py --add-mcp   # restore elastic-memory to mcp.json (before Act 2)
```
Story-order recording flow: `git checkout .` codebase → `--prep` → record Act 1 → `--clean` →
record live-build → `--add-mcp` + `git checkout .` → restart Kiro, `/agent` → checkout-memory →
record Act 2/3. **A fresh Kiro session defaults to stock Kiro — you MUST re-select the agent or
the memory tools won't fire**; the bottom status line reading `checkout-memory` vs `Kiro` is
the tell. Kiro must be restarted after `--prep` and `--add-mcp`.

---

## Uncommitted git state (as of 2026-06-14)

```
 M demo_scripts/aws-summit-2026-demo-runbook.md        # Act 3 /agent re-select fix
 M demo_scripts/aws-summit-2026-navattic-shot-sheet.md # Act 3 /agent re-select fix
?? demo_scripts/player/                                # the whole player (4 files) — NEW
```
Nothing committed yet for the player. Suggested two commits: (1) the player, (2) the Act 3
`/agent` doc fixes. Jeff had not given the go-ahead to commit at handoff time.

Recent relevant commits: `5d2d6fc` shot-sheet write-path RESOLVED · `4c9feb1` write path works
(inputs under trigger) · `f622c5e` reframe Act 1 to policy-blind · `58191e2` demo redesign.

---

## Open TODOs

- **Decide + execute the demo change** (Jeff's next task — ask what's changing, then walk the
  sync map above).
- Commit the player + the Act 3 doc fixes.
- Player section-B human visual pass on the stage iTerm2 profile.
- Make GitHub repo public before June 17.
- Uday sync — Bedrock creds for blog code examples.
- New AWS blog post ("Building Memory-as-a-Service for AI Agents with Elastic and Amazon
  Bedrock") — structure outlined in CLAUDE.md.
- Full 60-min rehearsal before June 15.

## Hard-won gotchas (don't relearn these)

- Workflow `inputs` MUST be nested under the manual trigger, or Agent Builder derives an empty
  tool schema and the agent writes empty docs. (This was the write-path bug; now fixed.)
- **Verify writes by ES doc count, NOT the Kibana Conversations tab** — Kiro talks to Agent
  Builder via MCP tool calls, not the Converse API, so Kiro sessions don't show in Conversations.
- `mcp-sidecar/save-fact-server.py` is an **insurance fallback** local MCP write path
  (Kiro-only) if the workflow tool ever breaks — not used in the current working demo.
- Jina embeddings, **never** say ELSER. `fact_semantic` must be set explicitly on write (not
  auto-copied from `fact`). **No DynamoDB anywhere** (AWS Summit competitive look).
- Kibana REST API needs **Basic auth** (KIBANA_USER/PASSWORD), not ES API keys; headers
  `kbn-xsrf: true`, `x-elastic-internal-origin: Kibana`, `Accept: application/json`. ES|QL
  tools need `params: {}` even when empty.
- "No custom MCP server" is the talk's core message — Agent Builder's native MCP endpoint IS
  the server.
- Credentials live in `.env` (gitignored) — never display them in chat.
