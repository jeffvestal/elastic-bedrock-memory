# Demo Capture Status — AWS Summit NYC 2026

Tracks which replay beats have real captured output vs. reconstructed placeholders.
**Act 2 and Act 3 are verbatim from the 2026-06-11 capture — do not re-record.**

---

## Still Needs Real Capture

| Beat # | Label | How to capture |
|--------|-------|----------------|
| 0 | `act1-placeholder` | Run stock Kiro (no MCP wired) with the refund prompt. Capture the full response. Replace `REPLAY_BEATS[0]["fragments"]` with the real output. **This is the only beat that truly matters for the demo story.** |
| 1 | `live-build: create-indices` | Run `python3 setup/create-indices.py` and capture stdout. Update `LIVE_BUILD_INDICES_OUT` lines in `content.py`. |
| 2 | `live-build: create-agent` | Run `python3 setup/create-agent.py` and capture stdout. Update `LIVE_BUILD_AGENT_OUT` lines in `content.py`. |
| 3 | `live-build: seed` | Run `python3 demo-data/seed.py` and capture stdout. The current reconstructed output says `68 docs` — verify the real count matches. |
| 4 | `wire: open mcp.json in vi` | Visual only — confirm the simulated vi edit looks right on the stage terminal. No code change needed unless the real file structure differs. |
| 5 | `wire: start kiro` | The Kiro ASCII banner is exact (pulled from real output). Just do a visual pass at stage terminal size to confirm it renders cleanly. |
| 6 | `wire: restart Kiro, select agent` | The `/agent` picker UX — confirm `● Switched to agent: checkout-memory` is the real output text. |

**Priority:** Beat 0 (Act 1) is the only blocker. Beats 1–3 are low-risk; the reconstructed output is plausible and the audience won't know if a line count is slightly off. Beats 4–6 are cosmetic.

---

## Verbatim — Do Not Re-Record

These beats are from the real 2026-06-11 Kiro session capture. Content is exact.

| Beat # | Label | Source |
|--------|-------|--------|
| 7 | `Act 2 — refund ask (memory)` | Verbatim capture |
| 8 | `Act 2 — plan (team decisions)` | Verbatim capture |
| 9 | `Act 2 — write models.py` | Verbatim capture |
| 10 | `Act 2 — write payments.py` | Verbatim capture |
| 11 | `Act 2 — write checkout.py` | Verbatim capture |
| 12 | `Act 2 — verify + summary` | Verbatim capture |
| 13 | `Act 2 — write beat (fix idempotency key)` | Verbatim capture |
| 14 | `response: Act 2 — write beat (save UUID rule)` | Verbatim capture — includes `save-knowledge-fact` call with fact ID `Wn9ktp4B` |
| 15 | `Act 3 — fresh session, select agent` | Verbatim capture |
| 16 | `Act 3 — read-back (teammate)` | Verbatim capture |
| 17 | `Act 3 — answer` | Verbatim capture |

---

## How to Slot In a Real Capture

1. Run `python3 ../player/replay.py --list` to confirm beat numbers.
2. Edit `../player/content.py` — find the beat's `fragments` list and replace reconstructed fragments with real output using `line()`, `tool()`, `write()`, `code()` etc.
3. Run `python3 ../player/selftest.py` — must stay 16/16.
4. Visual pass: `python3 ../player/replay.py --from-beat <N>`.

For Act 1 specifically: mirror how `ACT2_SEARCH`, `ACT2_PLAN`, etc. are structured in `content.py`. The placeholder is `REPLAY_BEATS[0]` with label `act1-placeholder`.
