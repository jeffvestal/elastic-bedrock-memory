# Demo Player — a fake Kiro terminal you drive with the arrow keys

A scripted terminal "movie" for the AWS Summit hands-on demo. It runs **inside your real
iTerm2**, so the window/font/theme are genuinely real — the program only reproduces Kiro's
in-terminal rendering and animates the typing + streaming. No network, no real Kiro, no real
scripts. Fully deterministic. It replaces the live demo / Navattic recording.

## Run it

```bash
python3 demo_scripts/player/play.py                  # full run from the top
python3 demo_scripts/player/play.py --list            # print the step index -> label map
python3 demo_scripts/player/play.py --from-step 14    # jump in (use --list to find N)
python3 demo_scripts/player/play.py --speed 1.5       # faster typing/streaming
python3 demo_scripts/player/play.py --render-all       # auto-play the whole thing (no keys)
python3 demo_scripts/player/play.py --render-all --speed 0   # instant dump (headless/debug)
```

## On stage — keymap

| Key | Does |
|-----|------|
| **→ (right)** | Play the next step. The model is **two presses per turn**: press once → the prompt **types out**; press again → that's **Enter**, the response **streams in**, then stops. |
| **→ mid-animation** | **Fast-forward**: drains the rest of the current step instantly (never skips output). Handy if a stream is running long while you talk. |
| **← (left)** | Step back one step (re-renders instantly). Recovery for an over-advance. |
| **mouse / trackpad scroll** | Native iTerm2 scrollback — scroll up to show earlier output mid-talk. Works because the player stays on the normal screen buffer. |
| **q** / **Ctrl-C** | Quit and restore the terminal. |

The window/tab **title** shows your position (`demo-player 7/29 — next: …`) so you always know
where you are without cluttering the screen.

### Stage tips
- Set the iTerm2 window first; the player adapts to its width (rules/status line/wrap).
- For a re-take of one act, `--list` to find the index, then `--from-step N`.
- Right-arrow is the only key you need for a clean linear run.

## What it covers

Full hands-on portion, in story order: **Act 1** (amnesiac stock Kiro builds the refund
endpoint policy-blind) → **live-build** (`create-indices` / `create-agent` / `seed`) →
**wire** (`--add-mcp`, `/agent`) → **Act 2** (memory-wired Kiro: searches first, cites the
sessions, builds it right, then the write beat) → **Act 3** (fresh session reads the saved
rule back).

## Editing the script

All content is data in **`content.py`** — the engine (`play.py`) is generic.

- A demo is `STEPS` (a flat list). `SEGMENTS` exposes each act for the self-test.
- Build turns with the helpers: `kiro_launch`, `kiro_turn`, `kiro_idle_end`, `shell_cmd`.
- Compose output from fragments: `line`, `blank`, `rule`, `tool`, `toolline`, `write`,
  `code`, `footer`, `banner`, `status`, `idle`, `sessionend` (defined in `play.py`).
- Tweak the **palette** and **timing** constants at the top of `play.py` to match a Kiro
  screenshot exactly or change the pace.

### Verbatim vs reconstructed
Act 2 + Act 3 are **verbatim** from the 2026-06-11 capture. Act 1, the live-build output,
and the wire step are **reconstructed** and marked `# RECONSTRUCTED — swap for real capture`
in `content.py`. To upgrade fidelity, run the real thing once and paste the captured output
over that segment's fragment list.

## Verify after editing

```bash
python3 demo_scripts/player/selftest.py
```

Runs without a TTY or network. Checks schema, render, the two-press structure, the
act-contrast invariants (Act 1 makes no `search-knowledge-facts` call; Act 2 searches +
saves + writes three files; Act 3 reads back), verbatim-token fidelity, the Act 1 policy
gaps, key decoding (including the lone-ESC no-hang case), fast-forward drain, and a real-pty
smoke test. Exits non-zero on any failure.

## Notes / non-goals

- It's a player, not a terminal emulator — it doesn't talk to a shell or to Kiro.
- The status line is rendered **inline** (it scrolls with the content) rather than pinned to
  the bottom — pinning would require the alternate screen, which breaks native scrollback.
  Inline flow is the deliberate trade-off that keeps scroll-up working like a real terminal.
- Code blocks render plain (dim), matching how Kiro shows them — no `rich` dependency.
