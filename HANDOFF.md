# Handoff — elastic-bedrock-memory (AWS Summit NYC 2026)

**Updated:** 2026-06-15 (pre-commit, about to commit + push)
**Talk:** From Stateless to Stateful: Architecting Agent Memory with Elastic and Bedrock
**Event:** AWS Summit NYC, June 17, 2026 (60 min solo)
**Repo:** github.com/jeffvestal/elastic-bedrock-memory (private — make public before June 17)

> Standing facts (infra, credentials, indices, key technical decisions) live in **CLAUDE.md**.
> This file is the *current state + what's in flight*. Read CLAUDE.md first, then this.

---

## TL;DR — where things stand

1. **The demo is fully built and was live-verified end-to-end on 2026-06-11.** Act 1 amnesiac →
   live-build → wire → Act 2 memory build + write beat → Act 3 cross-session read-back. Both
   read and write paths confirmed through Kiro.
2. **The stage player is `replay.py`** (split-screen: left = scrolling Kiro transcript, right =
   presenter notes). **25 beats.** Selftest is green (**15/16 pass, 1 harmless SKIP**).
3. **Player is ready to commit.** All six `demo_scripts/player/` files are modified and have been
   through selftest. See "What changed — two sessions" below.
4. **🔜 NEXT: stage visual pass on real iTerm2 profile.** Several fixes (typing feel, approval
   pause, vi takeover, flicker) can only be judged on a live TTY. Then rehearsal.

---

## What changed — this session pair (2026-06-15)

All in `demo_scripts/player/` (`replay.py`, `engine.py`, `content.py`, `notes.py`, `selftest.py`).

### Session A — player mechanics + verbatim capture

1. **Char-by-char prompt typing.** Typed prompts animate one char at a time (~35ms/char, not
   scaled by `--speed`; instant at `--speed 0`).
2. **Two-press model.** Press 1 types prompt and pauses (`→ run`); press 2 streams response.
   `_half_beat` flag. `←` during pause cancels.
3. **Kiro launch beat + banner.** Act 1 opens at shell prompt, you type `kiro-cli`, ASCII banner
   renders.
4. **Default speed = 0.25** (was 1.0).
5. **Prompt wrapping.** Long prompts wrap inside left pane (hanging indent under `> ` prefix).
6. **vi is a full-screen takeover.** Wire beat: press 1 types `vi …`, press 2 opens clean editor
   view (left pane = mcp.json buffer; `elastic-memory` block green; `~` filler rows; vi status),
   press 3 = `:wq`. Auth always renders `Basic ‹redacted›`.
7. **Flicker fix.** `_repaint` no longer does full `\x1b[2J`. Homes cursor, overwrites each row
   in place with `\x1b[K`, clears below with `\x1b[J`.
8. **Blank line before each typed prompt.** Footer no longer butts against next prompt.
9. **Staged approval dialogs.** Single `permbreak` → two staged dialogs (`permbreak(path,
   stage="trust")` then `stage="scope"`). Player pauses at each (`→ approve`).
10. **Act 1 made verbatim from 2026-06-15 real Kiro capture** — real diffs, real file line
    numbers, real footers. ACT1_WARMUP_RESPONSE (4-file read, 3 questions, `0.17 • 17s`) and
    ACT1_RESPONSE (13-line models.py, 14-line payments.py, 44-line endpoint at L112, main.py,
    `1.06 • 2m 59s`).
11. **Act 2 verbatim from 2026-06-11 real Kiro run** — real fact IDs, 6 files read, real diffs,
    footer `0.89 • 7m 24s`. Fact ID throughout: `Wn9ktp4BniyjIMohO9V5`.

### Session B — MCP dialogs + Act 1 correction beats

12. **`mcpbreak` fragment.** First time a read MCP tool fires, the player pauses on an approval
    dialog ("❯ Yes, single permission" highlighted first — matches real Kiro MCP UX, opposite of
    write `permbreak` which highlights "Trust" first). `engine.py`: `mcpbreak(tool_name)` factory
    + renderer. `replay.py`: `_stream_beat_frags` pauses on both `permbreak` and `mcpbreak`.
13. **`thinking()` fragment.** Renders `≡ Thinking... (esc to cancel)` in dim style while agent
    processes tool results.
14. **Collapsed MCP tool results.** Act 2 `search-knowledge-facts` responses render collapsed like
    real Kiro: `{ "content": [ { ...+5 lines (ctrl+o to toggle) }`. selftest ch14 has an allowlist
    for this beat.
15. **Act 1 expanded: 4 beats → 7 beats.** Added 3 correction turns (verbatim 2026-06-15 capture):
    - **Correction 1 (cap):** Jeff: "lets me refund more than the order." Kiro adds cumulative cap
      check + `func` import. **Key stays broken** (`refund-{order_id}-{amount_cents}`).
    - **Correction 2 (90-day window):** Jeff: "no time limit." Kiro adds 90-day guard + 422.
    - **Correction 3 (idempotency key):** Jeff: "two $10 refunds would collide." Kiro **actually
      writes the fix** — switches to `f"refund-{uuid.uuid4()}"`. This is the closing argument:
      "3 corrections, 3 policies, none in the codebase, all in memory."
16. **Notes updated** for all new/changed beats. Corrections 1 and 3 notes were rewritten to match
    the corrected narrative (correction 1 no longer says "self-corrects the key"; correction 3 now
    describes the real fix, not "already done").

**selftest result after all changes:** 15/16 PASS, 1 SKIP (golden snapshot — harmless).

---

## The terminal player — `replay.py` (the thing you'll most likely edit)

**Files:** `demo_scripts/player/` — `replay.py` (split-screen player + CLI), `engine.py` (shared
core: palette, timing, fragment factories, `fragment_to_lines`, key decode), `content.py` (the
demo as data: `REPLAY_BEATS` + `STEPS`/`SEGMENTS`), `notes.py` (right-pane commentary per beat),
`selftest.py` (16-check harness), `play_classic.py` (old single-pane player), `play.py` (shim).

**Run:** `python3 demo_scripts/player/replay.py`
- `--list` — print beat index → act → label map
- `--from-beat N` — jump in at beat N
- `--speed X` — animation multiplier (**default 0.25**; 0 = instant; >0.25 faster)
- `--render-all [--speed 0]` — headless auto-play (no TTY); used by selftest
- `--no-color` — plain text

**Keys:** `→` advance (two-press per prompt beat) · `←` back / cancel · `↑↓` or mouse-wheel
scroll the left pane · `q`/Ctrl-C quit. `→` during streaming = drain (fast-forward, never skips
output).

**Interaction model (keep it):**
- **Prompt beat:** press 1 types the prompt (char-by-char, wraps) and pauses (`→ run`); press 2
  streams the response. No-prompt beats stream on a single press.
- **vi beat:** press 1 types `vi …`; press 2 opens the fullscreen editor (`→ :wq write & quit`);
  press 3 pops back to the shell.
- **Approval dialogs:** stream pauses at each (`→ approve`); `→` to approve and continue.
  Write tools: `permbreak` (2 staged dialogs, "Trust" highlighted first).
  MCP read tools: `mcpbreak` (1 dialog, "Yes, single permission" highlighted first).

**Layout / compositor:** left pane ≈ 60% (scrolling transcript), right pane ≈ 40% (presenter
notes), `│` divider, header (act · beat label), footer (context-sensitive hints). `_repaint`
builds the whole frame and writes it atomically. State flags: `_half_beat` (prompt shown, awaiting
"enter"), `_in_fullscreen` (vi takeover), `_awaiting_approval` (paused on a dialog).

**⚠️ replay.py uses the ALTERNATE screen + mouse reporting** (`\x1b[?1049h`, `\x1b[?1000h`,
`\x1b[?1006h`). This is **deliberately different** from `play_classic.py`. Don't apply the
classic player's no-alt-screen invariant here. The split-screen needs the alt screen; scrollback
is handled in-pane via `↑↓`/wheel.

**Content model (`content.py`):**
- `REPLAY_BEATS` — 25 ordered beat dicts. Each: `label` (unique; must match a `NOTES` key),
  `act`, `prompt` (str or `None`), optional `prefix` (shell vs `  > `), optional `fullscreen`/
  `vi_status`, and `fragments` (list of fragment dicts).
- `STEPS` / `SEGMENTS` — older flat step model for `play_classic.py` + several selftests.
- Fragments: `line / blank / rule / tool / toolline / write / code / footer / banner / status /
  idle / sessionend / permbreak / mcpbreak / thinking`. Compose turns with `kiro_launch /
  kiro_turn / kiro_idle_end / shell_cmd`.
- `notes.py` — `NOTES[beat_label] = {"headline", "bullets":[…]}`; **every beat needs an entry**
  (selftest enforces).

**Verbatim vs reconstructed:**
- **Verbatim:** Act 1 initial response + warmup (2026-06-15 capture), Act 1 corrections 1–3
  (2026-06-15 capture), Act 2 (2026-06-11 capture), Act 3 (2026-06-11 capture). Fact ID
  `Wn9ktp4BniyjIMohO9V5` throughout Act 2/3.
- **Reconstructed:** live-build script output, wire/`--add-mcp` output, `/agent` picker
  (simplified), vi buffer (`VI_SCREEN`).
- Detailed status: `demo_scripts/aws-summit-2026-capture-status.md`.

**Verification discipline:** after any player change run `python3 demo_scripts/player/selftest.py`
(no TTY/network). 16 checks: schema, render smoke, two-press structure, act-contrast invariants,
Act 2/3 verbatim fidelity, Act 1 gap fidelity (initial response only — not corrections), key
decode (+ lone-ESC), fast-forward drain, restore sanity, no-rich, PTY smoke, replay note coverage,
vi-beat safety (no real token), expanded tool calls (collapsed for mcpbreak beats, expanded for
save/search facts), headless render-all, golden snapshot. **Expected: 15 pass + 1 SKIP.**

---

## ⚠️ The sync map — change these together when the demo changes

| Artifact | Path | Holds |
|---|---|---|
| Seeded memory (facts + conversations) | `demo-data/seed.py` | The 10 sessions / 18 facts the agent retrieves. **Source of truth for what's "in memory."** |
| Reference refund impls | `demo_scripts/reference/refunds-amnesiac.py`, `refunds-correct.py` | Wrong (policy-blind) and right (policy-aware) target code. |
| Capture run-book | `demo_scripts/aws-summit-2026-demo-runbook.md` | Source of truth for exact prompts, act flow, reset procedures. |
| Capture status | `demo_scripts/aws-summit-2026-capture-status.md` | Per-beat verbatim vs reconstructed tracking. |
| Practice guide / shot sheet / FAQ | `demo_scripts/aws-summit-2026-*.md` | Stage script, (legacy) Navattic shots, FAQ segment. |
| **Player content** | `demo_scripts/player/content.py` | The scripted replay (`REPLAY_BEATS`). |
| **Player notes** | `demo_scripts/player/notes.py` | Right-pane commentary — one entry per beat. |
| Slide deck | Google Slides `151FhokgExhlNBw1FuqPwyYVWVvlyKHfAJVBUiYUYUK4` | 22 slides + speaker notes (work copy). |

**After any demo-content change:** reseed (`python3 setup/demo-setup.py --reset`), re-verify the
read/write path through Kiro, update `content.py` **and** `notes.py`, run `selftest.py`, then
update the run-book + deck.

---

## The demo narrative (what the player depicts) — current version

ONE coding task built twice: **add a refund endpoint** to a FastAPI checkout service
(`~/repos/checkout-service-demo`, **separate repo**; reset between takes with
`git -C ~/repos/checkout-service-demo checkout .`).

- **Act 1 — amnesiac (stock Kiro):** warmup turn (reads repo, asks 3 questions) → refund turn:
  gets code patterns right but is **policy-blind** — ships `refund-{order_id}-{amount_cents}` key,
  no cap, no 90-day window. Then **3 manual correction turns**: (1) cap + func import, (2) 90-day
  guard, (3) idempotency key fixed to `uuid.uuid4()`. Each correction is a policy the agent could
  have read from memory. The closing note: 3 corrections, 3 policies, all from past sessions.
- **Live-build:** `create-indices.py` → `create-agent.py` → `seed.py` on camera.
- **Wire:** `vi` mcp.json (add `elastic-memory` block) → restart `kiro-cli` → `/agent` →
  checkout-memory.
- **Act 2 — memory Kiro:** SAME prompt → calls `search-knowledge-facts` (MCP approval dialog
  fires first use) → cites sessions → builds it right (cap + 90-day window + cents + JWT + UUID
  key). Then the **write beat**: saves the new idempotency convention via `save-knowledge-fact`
  (fact `Wn9ktp4BniyjIMohO9V5`).
- **Act 3 — fresh session:** `/agent` → checkout-memory, asks the idempotency convention →
  reads back the just-saved UUID rule. Proves write→read loop.

**Seeded decisions that make it land** (`seed.py`): money = integer cents (sess-005), JWT on
every route (sess-002), Stripe idempotency key (sess-004/007), Aurora PostgreSQL (sess-001),
refund policy = cumulative cap + 90-day window (sess-004), recent observability (sess-010).
10 sessions / 18 facts / ~40 conversation turns (68 docs total).

---

## Setup / reset commands (full detail in CLAUDE.md + run-book)

```bash
python3 setup/demo-setup.py             # status check (all green when healthy)
python3 setup/demo-setup.py --setup     # first-time: workflow + agent (enables write path)
python3 setup/demo-setup.py --reset     # wipe docs + reseed (clean 18 facts) + recreate agent
python3 setup/demo-setup.py --clean     # empty Elastic for the live-build capture (keeps workflow)
python3 setup/demo-setup.py --prep      # remove elastic-memory from mcp.json (Act 1 amnesia)
python3 setup/demo-setup.py --add-mcp   # restore elastic-memory to mcp.json (before Act 2)
```
Story-order recording flow: `git checkout .` codebase → `--prep` → record Act 1 → `--clean` →
record live-build → `--add-mcp` + `git checkout .` → restart Kiro, `/agent` → checkout-memory →
record Act 2/3. **A fresh Kiro session defaults to stock Kiro — you MUST re-select the agent or
the memory tools won't fire**; the bottom status line reading `checkout-memory` vs `Kiro` is the
tell. Restart Kiro after `--prep` and `--add-mcp`.

---

## Open TODOs

- **Stage visual pass on the real iTerm2 profile** — typing feel, approval pause, vi takeover,
  flicker, color/glyph/pacing. Run `python3 demo_scripts/player/replay.py`, walk each beat live.
- Make GitHub repo public before June 17.
- Uday sync — Bedrock creds for blog code examples.
- New AWS blog post ("Building Memory-as-a-Service for AI Agents with Elastic and Amazon
  Bedrock") — structure outlined in CLAUDE.md.
- Full 60-min rehearsal (before June 15… do it now).

---

## Hard-won gotchas (don't relearn these)

- `replay.py` uses the **alternate screen** — that's correct; "normal screen only" was a
  `play_classic.py` constraint, not replay's.
- Workflow `inputs` MUST be nested under the manual trigger, or Agent Builder derives an empty
  tool schema and the agent writes empty docs. (Was the write-path bug; fixed.)
- **Verify writes by ES doc count, NOT the Kibana Conversations tab** — Kiro talks to Agent
  Builder via MCP tool calls, not the Converse API, so Kiro sessions don't show in Conversations.
- Jina embeddings, **never** ELSER. `fact_semantic` must be set explicitly on write.
  **No DynamoDB anywhere** (AWS Summit competitive look).
- Kibana REST API needs **Basic auth** (KIBANA_USER/PASSWORD), not ES API keys; headers
  `kbn-xsrf: true`, `x-elastic-internal-origin: Kibana`, `Accept: application/json`. ES|QL tools
  need `params: {}` even when empty.
- "No custom MCP server" is the talk's core message — Agent Builder's native MCP endpoint IS the
  server.
- Credentials live in `.env` (gitignored) — never display them in chat. The vi beat's auth value
  must always render as `Basic ‹redacted›` (selftest enforces; never paste a real token).
- **`rtk-rewrite.sh` hook integrity failure** trips some Bash commands (grep exits 1). Workaround:
  use Read tool or `python3 -c`. To fix: `rtk init -g --auto-patch`.
- **Act 1 correction flow (important for narrative):** Correction 1 = cap only (key still broken).
  Correction 2 = 90-day window only. Correction 3 = idempotency key actually fixed here. Do NOT
  let correction 1 self-fix the key — that collapses the 3-correction narrative into 2.
- **`mcpbreak` vs `permbreak`:** MCP read-tool dialog highlights "Yes, single permission" first.
  Write-tool dialog highlights "Trust" first. They are different and must stay that way — it
  matches real Kiro UX.
- **selftest check 6 (Act 1 gap fidelity) only checks `ACT1_RESPONSE`**, not the correction
  beats — the corrections legitimately contain "90-day", "cap", etc. and should not be flagged.
