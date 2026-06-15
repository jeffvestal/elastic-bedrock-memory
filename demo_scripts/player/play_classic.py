"""
play_classic.py — the original fake-terminal player (renamed from play.py).

Replays the AWS Summit hands-on demo as a scripted "movie" that looks like a real Kiro CLI
session in iTerm2. Driven by the arrow keys (two presses per turn).

Interaction model:
  Right arrow #1  -> the next input TYPES OUT (character by character), no submit.
  Right arrow #2  -> that's ENTER: the response STREAMS IN, then stops.
  Right (mid-run) -> fast-forward (drain) the current animation to completion.
  Left arrow      -> step back one step (re-renders instantly; recovery for over-advance).
  q / Ctrl-C      -> quit and restore the terminal.
  Mouse/trackpad  -> native iTerm2 scrollback (we stay on the normal screen buffer).

Run:
  python3 demo_scripts/player/play_classic.py                 # full run from the top
  python3 demo_scripts/player/play_classic.py --from-step 14  # jump in (see --list)
  python3 demo_scripts/player/play_classic.py --list           # print step index -> label map
  python3 demo_scripts/player/play_classic.py --render-all     # auto-play (no keys)
  python3 demo_scripts/player/play_classic.py --render-all --speed 0  # instant (headless)
  python3 demo_scripts/player/play_classic.py --speed 1.5      # faster

No network, no .env, no real Kiro — pure offline playback.
"""
from __future__ import annotations

import argparse
import os
import select
import shutil
import signal
import sys
import termios
import time
import tty

from engine import (
    RESET, PALETTE, T_CHAR, T_WORD, T_LINE, T_TOOL, T_GAP, ESC_TIMEOUT,
    KIRO_BANNER, BANNER_WELCOME,
    Quit, decode_key,
    # fragment + step factories (re-exported so "from play_classic import ..." works)
    line, blank, rule, tool, toolline, write, code, footer, banner, status, idle, sessionend,
    step_input, step_stream, step_instant,
)


# ---------------------------------------------------------------------------
# The classic Player — unchanged behavior from original play.py.
# ---------------------------------------------------------------------------
class Player:
    def __init__(self, steps, out=None, color=True, speed=1.0, width=None):
        self.steps = steps
        self.color = color
        self.speed = speed
        self._out = out or (lambda s: (sys.stdout.write(s), sys.stdout.flush()))
        self._fixed_width = width
        self._fd = sys.stdin.fileno()
        self._saved_termios = None

    # -- styling -----------------------------------------------------------
    def c(self, s, style):
        if not self.color or not style:
            return s
        code_str = PALETTE.get(style, "")
        return f"{code_str}{s}{RESET}" if code_str else s

    def width(self):
        if self._fixed_width:
            return self._fixed_width
        return shutil.get_terminal_size((100, 30)).columns

    def out(self, s):
        self._out(s)

    # -- terminal + keys (real run only) ----------------------------------
    def _read_byte(self):
        try:
            return os.read(self._fd, 1).decode("utf-8", "ignore")
        except OSError:
            return ""

    def _wait_ready(self, timeout):
        try:
            r, _, _ = select.select([self._fd], [], [], timeout)
            return bool(r)
        except (OSError, ValueError):
            return False

    def read_key(self):
        return decode_key(self._read_byte, self._wait_ready)

    def setup_terminal(self):
        self._saved_termios = termios.tcgetattr(self._fd)
        tty.setcbreak(self._fd)  # keeps ISIG -> Ctrl-C still raises SIGINT

    def restore_terminal(self):
        if self._saved_termios is not None:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved_termios)
            self._saved_termios = None

    def set_title(self, t):
        if self.color:
            self.out(f"\x1b]0;{t}\x07")

    # -- emit units: each step is a generator of (text, delay) -------------
    def iter_step(self, step):
        kind = step["kind"]
        if kind == "input":
            yield (step.get("prefix", ""), 0.0)
            for ch in step["text"]:
                yield (self.c(ch, "user"), T_CHAR)
            # no newline — the "enter" press (next step) supplies it
        elif kind == "stream":
            yield ("\n", 0.0)
            for frag in step["fragments"]:
                yield from self.iter_fragment(frag)
        elif kind == "instant":
            for frag in step["fragments"]:
                yield from self.iter_fragment(frag)

    def iter_fragment(self, f):
        t = f["t"]
        if t == "blank":
            yield ("\n", 0.0)
        elif t == "rule":
            yield (self.c("─" * self.width(), "rule") + "\n", T_LINE)
        elif t == "line":
            indent = " " * f.get("indent", 2)
            style = f.get("style", "text")
            s = f["s"]
            if f.get("stream", True) and s:
                # Stream word-by-word, wrapping with a hanging indent (matches Kiro).
                maxw = max(20, self.width())
                yield (indent, 0.0)
                col = len(indent)
                words = s.split(" ")
                for i, w in enumerate(words):
                    if col + len(w) > maxw and col > len(indent):
                        yield ("\n" + indent, 0.0)
                        col = len(indent)
                    last = (i == len(words) - 1)
                    chunk = w if last else w + " "
                    yield (self.c(chunk, style), T_WORD)
                    col += len(w) + (0 if last else 1)
                yield ("\n", 0.0)
            else:
                yield (self.c(indent + s, style) + "\n", T_LINE)
        elif t == "tool":
            dot = self.c("●", "tool")
            yield (f"{dot} {self.c(f['name'], 'tool')}\n", T_LINE)
            if f.get("arg"):
                yield (self.c(f"    ╰ {f['arg']}", "dim") + "\n", T_TOOL)
            else:
                yield ("", T_TOOL)
        elif t == "toolline":
            dot = self.c("●", "tool")
            yield (f"{dot} {f['label']}\n", T_LINE)
            if f.get("detail"):
                yield (self.c(f"    {f['detail']}", "dim") + "\n", T_TOOL)
            else:
                yield ("", T_TOOL)
        elif t == "write":
            dot = self.c("●", "tool")
            yield (f"{dot} {self.c('Write', 'tool')} {f['path']}\n", T_LINE)
            yield (self.c("  " + f["summary"], "dim") + "\n", T_LINE)
            for sign, lineno, content_str in f["diff"]:
                yield (self._diff_line(sign, lineno, content_str) + "\n", T_LINE)
            yield ("", T_GAP)
        elif t == "code":
            indent = " " * f.get("indent", 2)
            for ln in f["lines"]:
                yield (self.c(indent + ln, "dim") + "\n", T_LINE)
            yield ("", T_GAP)
        elif t == "footer":
            txt = f"▸ Credits: {f['credits']} • Time: {f['time']}"
            yield (self.c(txt, "dim") + "\n", T_GAP)
        elif t == "banner":
            yield (self.c(KIRO_BANNER, "banner") + "\n", 0.0)
            for ln in BANNER_WELCOME:
                yield (self.c(ln, "dim") + "\n", 0.0)
        elif t == "status":
            w = self.width()
            left = f"  {f['agent']} · {f['model']} · {f['ctx']}"
            right = f"{f['cwd']} · ({f['branch']})  "
            pad = max(1, w - len(left) - len(right))
            yield (self.c(left + " " * pad + right, "status") + "\n", 0.0)
        elif t == "idle":
            yield (self.c("  ask a question or describe a task ↵", "dim") + "\n", 0.0)
            yield (self.c("  Press Ctrl+C or Ctrl+D again to exit", "dim") + "\n", 0.0)
        elif t == "sessionend":
            yield ("\n" + self.c("Session ended.", "dim") + "\n", 0.0)
            yield (self.c(f"Resume with: kiro-cli chat --resume-id {f['resume']}", "dim") + "\n", 0.0)
        else:
            yield (f"[unknown fragment: {t}]\n", 0.0)

    def _diff_line(self, sign, lineno, content_str):
        num = f"{lineno:>4}" if lineno != "" else "    "
        if sign == "+":
            return self.c(f"  {num}{sign}  {content_str}", "green")
        if sign == "-":
            return self.c(f"  {num}{sign}  {content_str}", "red")
        return self.c(f"  {num}   {content_str}", "dim")

    # -- playing -----------------------------------------------------------
    def _delay(self, base, instant):
        if instant or self.speed <= 0:
            return 0.0
        return base / self.speed

    def play_step(self, step, interactive):
        """Render one step. interactive=True watches for a key to fast-forward."""
        instant = (step["kind"] == "instant")
        skip = instant
        for txt, base_delay in self.iter_step(step):
            if txt:
                self.out(txt)
            d = self._delay(base_delay, skip)
            if d <= 0:
                continue
            if interactive:
                if self._wait_ready(d):
                    k = self.read_key()
                    if k == "QUIT":
                        raise Quit()
                    if k == "RIGHT":
                        skip = True  # drain the rest instantly — never skips output
                    # LEFT / others: ignore mid-animation
            else:
                # headless preview path: plain sleep (skipped entirely when speed==0)
                time.sleep(d)

    def render_range_instant(self, lo, hi):
        # Re-render a prefix of the demo with no animation (used by 'back').
        for s in self.steps[lo:hi]:
            for txt, _ in self.iter_step(s):
                if txt:
                    self.out(txt)

    # -- drivers -----------------------------------------------------------
    def render_all(self):
        """Auto-play every step with no key handling (preview / headless capture)."""
        for s in self.steps:
            self.play_step(s, interactive=False)

    def run(self, start=0):
        """Interactive arrow-driven run. Requires a real TTY."""
        self.setup_terminal()

        def _restore_and_exit(signum, frame):
            self.restore_terminal()
            self.out("\n")
            os._exit(0)

        signal.signal(signal.SIGINT, _restore_and_exit)
        signal.signal(signal.SIGTERM, _restore_and_exit)
        try:
            idx = start
            if start > 0:
                self.out("\x1b[H\x1b[J")
                self.render_range_instant(0, start)
            # render leading auto steps (e.g. the launch banner) before first key
            while idx < len(self.steps) and self.steps[idx].get("auto"):
                self.play_step(self.steps[idx], interactive=True)
                idx += 1
            self._title(idx)
            while idx < len(self.steps):
                key = self.read_key()
                if key == "QUIT":
                    break
                elif key == "RIGHT":
                    self.play_step(self.steps[idx], interactive=True)
                    idx += 1
                    while idx < len(self.steps) and self.steps[idx].get("auto"):
                        self.play_step(self.steps[idx], interactive=True)
                        idx += 1
                    self._title(idx)
                elif key == "LEFT":
                    idx = max(0, idx - 1)
                    self.out("\x1b[H\x1b[J")
                    self.render_range_instant(0, idx)
                    self._title(idx)
                # ESC / NONE / IGNORE: do nothing
        except Quit:
            pass
        finally:
            self.restore_terminal()
            self.out("\n")

    def _title(self, idx):
        n = len(self.steps)
        if idx < n:
            lbl = self.steps[idx].get("label") or self.steps[idx]["kind"]
        else:
            lbl = "end"
        self.set_title(f"demo-player {idx}/{n} — next: {lbl}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _load_steps():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import content
    return content.STEPS


def main(argv=None):
    p = argparse.ArgumentParser(description="Classic fake terminal demo player (Kiro look-alike).")
    p.add_argument("--from-step", type=int, default=0, help="start at this step index (see --list)")
    p.add_argument("--list", action="store_true", help="print step index -> label map and exit")
    p.add_argument("--render-all", action="store_true", help="auto-play every step (no keys); pair with --speed 0 for instant")
    p.add_argument("--speed", type=float, default=1.0, help="animation speed multiplier (0 = instant)")
    p.add_argument("--no-color", action="store_true", help="disable ANSI color")
    args = p.parse_args(argv)

    steps = _load_steps()

    if args.list:
        for i, s in enumerate(steps):
            lbl = s.get("label") or ""
            print(f"{i:>4}  {s['kind']:<8} {lbl}")
        return 0

    player = Player(steps, color=not args.no_color, speed=args.speed)

    if args.render_all:
        player.render_all()
        return 0

    if not sys.stdin.isatty():
        sys.stderr.write("play_classic.py needs a TTY for interactive mode. Use --render-all in a pipe.\n")
        return 2

    player.run(start=args.from_step)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
