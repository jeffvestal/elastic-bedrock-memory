# Demo Player — AWS Summit 2026

Two players live here. **`replay.py` is the main one for the stage.** `play_classic.py` is the
proven fallback if anything goes wrong.

---

## replay.py — the split-screen player (recommended)

Embraces that it's pre-recorded. Two-column layout: left = terminal transcript streaming in,
right = synced commentary (your stage cues + audience read-along). One right-arrow per beat,
17 beats total. No fake typing — the prompt appears as already-entered and the response streams.

```bash
python3 demo_scripts/player/replay.py                    # full run
python3 demo_scripts/player/replay.py --list              # beat index → label map
python3 demo_scripts/player/replay.py --from-beat 6       # jump in (0-indexed)
python3 demo_scripts/player/replay.py --speed 1.3         # faster streaming
python3 demo_scripts/player/replay.py --render-all --speed 0   # headless dump (CI)
```

### Keymap
| Key | Does |
|-----|------|
| **→ (right)** | Play the next beat. Output streams in; press again mid-stream to fast-forward (drain). |
| **← (left)** | Step back one beat (re-renders instantly). |
| **↑ / ↓** | Scroll the left transcript pane up/down (while paused). Advancing a beat returns to bottom. |
| **q** / **Ctrl-C** | Quit and restore the terminal (alt-screen exits cleanly). |

### Layout

```
┌ demo-replay  beat 7/17 · Act 2 — Memory Kiro ──────────────────────────────┐
│ LEFT (60%): terminal transcript          │ RIGHT (40%): commentary          │
│   kiro-cli                               │  HEADLINE (what's happening)     │
│   ● search-knowledge-facts               │                                  │
│     ╰ nlQuery=refund policy…             │  • detail bullet                 │
│   Good — I have the team decisions.      │  • detail bullet                 │
│                                          │  • detail bullet                 │
└ → next  ← back  ↑↓ scroll  q quit ──────────────────────────────────────────┘
```

The right pane reads as audience explanation but is really your stage cues. No visible labeling.

### Beat structure (17 beats)
| # | Act | Label |
|---|-----|-------|
| 0 | Act 1 | Placeholder (swap in real capture) |
| 1–3 | Live Build | create-indices / create-agent / seed |
| 4–5 | Wire | vi mcp.json edit / select agent |
| 6–13 | Act 2 | search → plan → models → payments → checkout → verify → fix → save |
| 14–16 | Act 3 | select agent → search → answer |

---

## play_classic.py — the original live-typed player (fallback)

The proven fallback. Same two-press interaction model as before: press 1 = prompt types out,
press 2 = Enter/response streams. Normal screen buffer (native iTerm2 scrollback preserved).

```bash
python3 demo_scripts/player/play_classic.py                  # full run
python3 demo_scripts/player/play_classic.py --list            # step index
python3 demo_scripts/player/play_classic.py --from-step 14    # jump in
python3 demo_scripts/player/play_classic.py --speed 1.5       # faster
python3 demo_scripts/player/play_classic.py --render-all --speed 0   # headless
```

---

## Verify after any edit

```bash
python3 demo_scripts/player/selftest.py
```

16 checks, no TTY or network needed. Covers: schema, render, two-press structure, act-contrast,
verbatim fidelity (Act 2/3), Act 1 policy gaps, key decoding, fast-forward drain, terminal
restore, no-rich, **replay note coverage**, **vi beat credential safety**, **expanded tool calls**,
**replay headless render**, **classic golden snapshot**. Exits non-zero on any failure.

---

## Files

| File | Purpose |
|------|---------|
| `replay.py` | The new split-screen player (main stage player) |
| `play_classic.py` | Original live-typed player (proven fallback) |
| `play.py` | Compatibility shim (`from engine import *`; `from play_classic import Player`) |
| `engine.py` | Shared core: palette, timing, fragment factories, `decode_key`, `fragment_to_lines` |
| `content.py` | Demo as pure data: `STEPS` (classic), `REPLAY_BEATS` (replay), `SEGMENTS` (selftest) |
| `notes.py` | Right-pane commentary: `NOTES = {beat_label: {headline, bullets}}` |
| `selftest.py` | 16-check verification harness |

---

## Editing the demo script

**Content is in `content.py`** — the engines are generic. For replay, edit `REPLAY_BEATS`. For
classic, the `SEGMENTS` / `STEPS` structure is unchanged. Edit notes in `notes.py`.

Fragment vocabulary (defined in `engine.py`): `line`, `blank`, `rule`, `tool`, `toolline`,
`write`, `code`, `footer`, `banner`, `status`, `idle`, `sessionend`.

**After any content change:** run `python3 demo_scripts/player/selftest.py` — 16 green.

### Verbatim vs reconstructed
Act 2 + Act 3 are **verbatim** from the 2026-06-11 capture (tool calls, fact IDs `sess-004-fact-2`,
`Wn9ktp4B`, the diffs). Act 1 is a **placeholder beat** (slot reserved). Live build, wire, and
the `/agent` picks are **reconstructed** (marked `# RECONSTRUCTED` in `content.py`).

### Act 1 slot
`REPLAY_BEATS[0]` has `label: "act1-placeholder"`. Drop in the real capture by replacing its
`fragments` list — mirroring how the Act 2 sub-lists are structured. Run selftest after.

---

## Stage tips

- Set the iTerm2 window to your stage profile *before* launching — the player adapts to the
  current terminal size on each beat and on SIGWINCH (window resize).
- `--list` to find a beat index, then `--from-beat N` to jump in for a re-take.
- Right-arrow is the only key for a clean linear run. Fast-forward mid-stream = drain instantly.
- If `replay.py` crashes and leaves the terminal weird: `reset` (shell command) restores it,
  and `play_classic.py` is the one-command fallback.
