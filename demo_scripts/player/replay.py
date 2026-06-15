"""
replay.py — two-column terminal replay player for the AWS Summit demo.

Left pane (60%): scrolling transcript — streams each beat's fragments.
Right pane (40%): presenter notes — headline + bullets for the current beat.

Interaction:
  Right arrow  → advance to next beat (streams it in)
  Left arrow   → step back one beat (instant re-render)
  Up / Down    → scroll the left pane ±1 row
  q / Ctrl-C   → quit and restore terminal

Run:
  python3 demo_scripts/player/replay.py                  # full run
  python3 demo_scripts/player/replay.py --list           # print beat index map
  python3 demo_scripts/player/replay.py --from-beat N    # jump to beat N
  python3 demo_scripts/player/replay.py --speed 1.5      # faster animation
  python3 demo_scripts/player/replay.py --render-all     # auto-play, no keys
  python3 demo_scripts/player/replay.py --render-all --speed 0  # instant
  python3 demo_scripts/player/replay.py --no-color       # plain text

No network, no .env required — pure offline playback.
"""
from __future__ import annotations

import argparse
import errno
import os
import select
import shutil
import signal
import sys
import termios
import textwrap
import tty

from engine import (
    RESET, PALETTE,
    T_LINE, T_WORD, T_TOOL, T_GAP, ESC_TIMEOUT,
    Quit, decode_key,
    fragment_to_lines, apply_color,
    # fragment factories (used by REPLAY_BEATS in content.py — re-exported for convenience)
    line, blank, rule, tool, toolline, write, code, footer, banner, status, idle, sessionend,
    step_input, step_stream, step_instant,
)


# ---------------------------------------------------------------------------
# Prompt wrapping — typed user input must wrap inside the left pane, not run
# off the screen past the divider.
# ---------------------------------------------------------------------------
def wrap_prompt_lines(prefix, text, width, color=True):
    """
    Wrap a typed prompt to `width`, hanging-indenting continuation lines under
    the prefix. First line = dim prefix + user-colored text; continuations =
    blank indent + user-colored text. Returns a list of styled strings.
    """
    hang = " " * len(prefix)
    avail = max(8, width - len(prefix))
    wrapped = textwrap.wrap(text, width=avail) if text else []
    if not wrapped:
        wrapped = [""]
    out = []
    for i, seg in enumerate(wrapped):
        if i == 0:
            out.append(apply_color(prefix, "dim", color) + apply_color(seg, "user", color))
        else:
            out.append(hang + apply_color(seg, "user", color))
    return out


# ---------------------------------------------------------------------------
# Right-pane note renderer
# ---------------------------------------------------------------------------
def render_note(note, width, color=True):
    """
    Render a note dict {"headline": str, "bullets": [str, ...], "commentary": str}
    into a list of styled strings (no \\n).

    Layout:
      - Headline (teal bold, larger feel via extra leading blank)
      - One blank separator
      - Bullets with a blank line between each for breathing room
      - If "commentary" present: separator rule, then wrapped prose (dim white)
    """
    c = lambda s, style: apply_color(s, style, color)
    lines = []
    if not note:
        return lines

    # Extra leading blank so headline doesn't butt against the top edge
    lines.append("")

    # Headline (teal + bold, wrapped)
    headline = note.get("headline", "")
    for part in textwrap.wrap(headline, width - 2) or [headline]:
        lines.append(c("  " + part, "headline"))

    lines.append("")  # blank separator

    # Bullets — one blank line between each for vertical breathing room
    bullets = note.get("bullets", [])
    for bi, bullet in enumerate(bullets):
        prefix = "  •  "
        wrapped = textwrap.wrap(bullet, width - len(prefix) - 1)
        if not wrapped:
            wrapped = [bullet]
        first = True
        for part in wrapped:
            if first:
                lines.append(c(prefix + part, "bullet"))
                first = False
            else:
                lines.append(c(" " * len(prefix) + part, "bullet"))
        if bi < len(bullets) - 1:
            lines.append("")  # spacing between bullets

    # Commentary blob (optional) — separated by a dim rule, wrapped prose
    commentary = note.get("commentary", "")
    if commentary:
        lines.append("")
        lines.append(c("  " + "─" * (width - 4), "rule"))
        lines.append("")
        for part in textwrap.wrap(commentary, width - 4) or [commentary]:
            lines.append(c("  " + part, "dim"))

    # Query box (optional) — "see it in Elastic" header + ES|QL lines
    queries = note.get("queries", [])
    if queries:
        lines.append("")
        lines.append(c("  " + "─" * (width - 4), "rule"))
        lines.append("")
        lines.append(c("  ↗ now: Kibana → ES|QL", "dim"))
        lines.append("")
        for q in queries:
            if q == "":
                lines.append("")
            else:
                lines.append(c("  " + q, "tool"))

    return lines


# ---------------------------------------------------------------------------
# Left-pane: build line buffer from a beat's fragments
# ---------------------------------------------------------------------------
def beat_to_lines(beat, width, color=True):
    """Render a beat's prompt + fragments into (styled_line, delay) pairs."""
    result = []
    if beat.get("prompt"):
        prefix = beat.get("prefix", "  > ")
        for pl in wrap_prompt_lines(prefix, beat["prompt"], width, color):
            result.append((pl, 0.0))
        result.append(("", 0.0))  # blank line between prompt and response
    for frag in beat.get("fragments", []):
        result.extend(fragment_to_lines(frag, width, color))
    return result


# ---------------------------------------------------------------------------
# Main Player class
# ---------------------------------------------------------------------------
class ReplayPlayer:
    def __init__(self, beats, notes, out=None, color=True, speed=1.0, render_all_mode=False):
        self.beats = beats
        self.notes = notes
        self.color = color
        self.speed = speed
        self._render_all_mode = render_all_mode

        # output function: for render-all we write directly to stdout
        if out is not None:
            self._out = out
        else:
            self._out = lambda s: (sys.stdout.write(s), sys.stdout.flush())

        self._fd = sys.stdin.fileno() if sys.stdin.isatty() else -1
        self._saved_termios = None
        self._restored = False
        self._needs_repaint = False
        self._size = None

        # Beat index and left-pane state
        self._beat_idx = 0
        self._line_buf = []   # accumulated styled lines (no \\n)
        self._scroll_offset = 0  # 0 = bottom, positive = scroll up
        self._half_beat = False  # True = prompt shown, waiting for "enter" press
        self._in_fullscreen = False  # True = vi-style full-pane takeover active
        self._awaiting_approval = False  # True = paused mid-stream on an approval dialog

        # Layout
        self._left_w = 72
        self._right_w = 48
        self._content_rows = 36

    # -------------------------------------------------------------------------
    # Terminal setup / teardown
    # -------------------------------------------------------------------------
    def _restore(self):
        if self._restored:
            return
        self._restored = True
        self._write_raw("\x1b[?1006l")    # disable SGR mouse
        self._write_raw("\x1b[?1000l")    # disable X10 mouse
        self._write_raw("\x1b[?25h")      # show cursor
        self._write_raw("\x1b[?1049l")    # leave alt screen
        if self._saved_termios and self._fd >= 0:
            try:
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved_termios)
            except Exception:
                pass

    def _write_raw(self, s):
        """Write directly to stdout (bypasses the _out callback)."""
        sys.stdout.write(s)
        sys.stdout.flush()

    def _setup_terminal(self):
        if self._fd < 0:
            return
        self._saved_termios = termios.tcgetattr(self._fd)
        tty.setcbreak(self._fd)

    def _install_signals(self):
        def _sig_handler(signum, frame):
            self._restore()
            os._exit(0)

        def _sigwinch(signum, frame):
            self._needs_repaint = True
            self._size = None

        signal.signal(signal.SIGINT, _sig_handler)
        signal.signal(signal.SIGTERM, _sig_handler)
        signal.signal(signal.SIGWINCH, _sigwinch)

    # -------------------------------------------------------------------------
    # Layout
    # -------------------------------------------------------------------------
    def _compute_layout(self):
        if self._render_all_mode:
            cols, rows = 160, 40
        else:
            cols, rows = shutil.get_terminal_size((120, 40))
        self._size = (cols, rows)
        self._left_w = max(20, int(cols * 0.60))
        self._right_w = max(20, cols - self._left_w - 1)  # -1 for divider
        self._content_rows = max(5, rows - 3)  # header + footer + 1 padding
        return cols, rows

    # -------------------------------------------------------------------------
    # Key reading
    # -------------------------------------------------------------------------
    def _read_byte(self):
        if self._fd < 0:
            return ""
        try:
            return os.read(self._fd, 1).decode("utf-8", "ignore")
        except OSError:
            return ""

    def _wait_ready(self, timeout):
        if self._fd < 0:
            return False
        while True:
            try:
                r, _, _ = select.select([self._fd], [], [], timeout)
                return bool(r)
            except OSError as e:
                if e.errno == errno.EINTR:
                    return False
                raise

    def _read_key(self):
        """Extended key reader: arrow keys + mouse scroll (X10 and SGR)."""
        b = self._read_byte()
        if b == "":
            return "NONE"
        if b in ("q", "Q", "\x03", "\x04"):
            return "QUIT"
        if b != "\x1b":
            return "IGNORE"
        # ESC sequence
        if not self._wait_ready(ESC_TIMEOUT):
            return "ESC"
        b2 = self._read_byte()
        if b2 not in ("[", "O"):
            return "IGNORE"
        b3 = self._read_byte()
        # Standard arrows
        if b3 in ("C", "D", "A", "B"):
            return {"C": "RIGHT", "D": "LEFT", "A": "UP", "B": "DOWN"}[b3]
        # X10 mouse: \x1b[M<cb><cx><cy>  (button 64/65 = scroll up/down)
        if b3 == "M" and b2 == "[":
            cb = self._read_byte()
            self._read_byte()  # cx (discard)
            self._read_byte()  # cy (discard)
            if cb:
                btn = ord(cb) - 32
                if btn == 64:
                    return "UP"
                if btn == 65:
                    return "DOWN"
            return "IGNORE"
        # SGR mouse: \x1b[<Cb;Cx;Cy{M|m}  (button 64/65 = scroll up/down)
        if b3 == "<" and b2 == "[":
            params = []
            while True:
                c = self._read_byte()
                if not c or c in ("M", "m"):
                    break
                params.append(c)
            try:
                btn = int("".join(params).split(";")[0])
                if btn == 64:
                    return "UP"
                if btn == 65:
                    return "DOWN"
            except (ValueError, IndexError):
                pass
            return "IGNORE"
        return "IGNORE"

    # -------------------------------------------------------------------------
    # Compositor — builds and writes a complete frame atomically
    # -------------------------------------------------------------------------
    def _pad(self, s, width):
        """Pad or truncate a styled string to exactly `width` visible chars."""
        # Strip ANSI to measure visible length
        import re
        visible = re.sub(r'\x1b\[[^A-Za-z]*[A-Za-z]', '', s)
        vlen = len(visible)
        if vlen < width:
            return s + " " * (width - vlen)
        elif vlen > width:
            # Truncate: need to cut visible chars while keeping leading escapes
            # Simple approach: rebuild char by char tracking visible count
            out = []
            count = 0
            i = 0
            while i < len(s) and count < width:
                if s[i] == '\x1b':
                    # consume escape sequence
                    j = i + 1
                    while j < len(s) and not s[j].isalpha():
                        j += 1
                    if j < len(s):
                        j += 1
                    out.append(s[i:j])
                    i = j
                else:
                    out.append(s[i])
                    count += 1
                    i += 1
            return "".join(out) + RESET
        return s

    def _repaint(self, beat_idx, line_buf, scroll_offset=0):
        cols, rows = self._size or self._compute_layout()
        c = lambda s, style: apply_color(s, style, self.color)
        n_beats = len(self.beats)
        at_end = beat_idx >= n_beats
        content_rows = self._content_rows

        # --- Header ---
        if at_end:
            hdr = f"  demo-replay  {n_beats}/{n_beats} beats · done — press q to quit"
        elif self._in_fullscreen:
            hdr = f"  vi · {self.beats[beat_idx].get('prompt', 'editing')}"
        else:
            act_label = self.beats[beat_idx]["act"]
            beat_label = self.beats[beat_idx]["label"]
            hdr = f"  demo-replay  beat {beat_idx + 1}/{n_beats} · {act_label} · {beat_label}"
        hdr_padded = self._pad(c(hdr, "dim"), cols)

        # --- Right-pane note (still shown during a fullscreen takeover) ---
        if at_end:
            note = {
                "headline": "Demo complete",
                "bullets": [
                    "All beats played.",
                    "← left arrow to step back through any beat.",
                    "q to quit.",
                ],
            }
        else:
            note_key = self.beats[beat_idx]["label"]
            note = self.notes.get(note_key, {})
        right_lines = render_note(note, self._right_w, self.color)

        # --- Left-pane content ---
        if self._in_fullscreen and not at_end:
            # vi-style takeover: render the editor buffer, then '~' filler rows,
            # and a status line on the last content row.
            screen = self.beats[beat_idx].get("fullscreen", [])
            vi_status = self.beats[beat_idx].get("vi_status", '"buffer" [+]')
            visible_left = []
            for text, style in screen:
                visible_left.append(c(text, style))
            while len(visible_left) < content_rows - 1:
                visible_left.append(c("~", "rule"))
            visible_left = visible_left[:content_rows - 1]
            visible_left.append(c("  " + vi_status, "status"))
        else:
            # Normal scrolling transcript window: bottom unless scrolled up.
            total_left = len(line_buf)
            start_idx = max(0, total_left - content_rows - scroll_offset)
            end_idx = max(0, total_left - scroll_offset)
            visible_left = line_buf[start_idx:end_idx]
            while len(visible_left) < content_rows:
                visible_left = [""] + visible_left

        divider = c("│", "rule")

        rows_out = [hdr_padded]
        for row in range(content_rows):
            left_line = visible_left[row] if row < len(visible_left) else ""
            right_line = right_lines[row] if row < len(right_lines) else ""
            left_padded = self._pad(left_line, self._left_w)
            right_padded = self._pad(right_line, self._right_w)
            rows_out.append(left_padded + divider + right_padded)

        # --- Footer — nav hints in the right column only, left stays blank ---
        if at_end:
            ftr = "  ← back  ↑↓/scroll  q quit"
        elif self._awaiting_approval:
            ftr = "  → approve  q quit"
        elif self._in_fullscreen:
            fs_type = self.beats[beat_idx].get("fullscreen_type", "vi")
            if fs_type == "picker":
                ftr = "  → select agent  ← cancel"
            else:
                ftr = "  → :wq write & quit  ← cancel"
        elif self._half_beat:
            ftr = "  → run  ← cancel  ↑↓/scroll  q quit"
        else:
            ftr = "  → next  ← back  ↑↓/scroll  q quit"
        ftr_left = " " * self._left_w
        ftr_right = self._pad(c(ftr, "dim"), self._right_w)
        rows_out.append(ftr_left + divider + ftr_right)

        # --- Atomic write, flicker-free ---
        # Home the cursor and overwrite each row in place (clear-to-EOL per line),
        # then clear anything left below. No full-screen \x1b[2J flash, no trailing
        # newline that would scroll the last row.
        out = ["\x1b[H"]
        for i, r in enumerate(rows_out):
            out.append(r + "\x1b[K")
            if i < len(rows_out) - 1:
                out.append("\n")
        out.append("\x1b[J")
        self._write_raw("".join(out))

    # -------------------------------------------------------------------------
    # Beat streaming
    # -------------------------------------------------------------------------
    def _stream_beat_frags(self, beat_idx, line_buf):
        """Stream this beat's fragments (prompt already in line_buf). RIGHT drains."""
        beat = self.beats[beat_idx]
        skip = False
        for frag in beat.get("fragments", []):
            flines = fragment_to_lines(frag, self._left_w, self.color)
            for (fline_text, delay) in flines:
                line_buf.append(fline_text)
                self._scroll_offset = 0
                self._repaint(beat_idx, line_buf, self._scroll_offset)
                if skip or self.speed <= 0:
                    continue
                d = delay / self.speed
                if d <= 0:
                    continue
                if self._wait_ready(d):
                    k = self._read_key()
                    if k == "QUIT":
                        raise Quit()
                    if k == "RIGHT":
                        skip = True  # drain remaining without skipping output
            # Approval dialogs block until the presenter arrows through them —
            # one pause per staged dialog. Honored even during fast-forward.
            # permbreak = write-tool approval; mcpbreak = MCP read-tool first-use approval.
            if frag.get("t") in ("permbreak", "mcpbreak"):
                self._await_approval(beat_idx, line_buf)
                skip = False  # resume normal pacing after the approval

        if self._needs_repaint:
            self._needs_repaint = False
            self._compute_layout()
            self._repaint(beat_idx, line_buf, self._scroll_offset)

    def _await_approval(self, beat_idx, line_buf):
        """Block on an approval dialog until the presenter presses → (approve).
        QUIT exits; other keys are ignored. The footer reads '→ approve'."""
        self._awaiting_approval = True
        self._repaint(beat_idx, line_buf, self._scroll_offset)
        try:
            while True:
                k = self._read_key()
                if k == "QUIT":
                    raise Quit()
                if k == "RIGHT":
                    break
                # LEFT/UP/DOWN/ESC/NONE: ignore — an approval only goes forward.
        finally:
            self._awaiting_approval = False

    # -------------------------------------------------------------------------
    # Re-render a prefix of beats instantly (for 'back' navigation)
    # -------------------------------------------------------------------------
    def _rebuild_line_buf(self, up_to_beat_idx):
        """Rebuild line_buf by instant-rendering beats 0..up_to_beat_idx-1."""
        buf = []
        for bi in range(up_to_beat_idx):
            beat = self.beats[bi]
            if beat.get("prompt"):
                prefix = beat.get("prefix", "  > ")
                if buf and buf[-1] != "":
                    buf.append("")  # separator from the previous turn
                for pl in wrap_prompt_lines(prefix, beat["prompt"], self._left_w, self.color):
                    buf.append(pl)
                buf.append("")  # blank line between prompt and response
            for frag in beat.get("fragments", []):
                for fline_text, _delay in fragment_to_lines(frag, self._left_w, self.color):
                    buf.append(fline_text)
        return buf

    # -------------------------------------------------------------------------
    # render_all — headless auto-play (no TTY required)
    # -------------------------------------------------------------------------
    def render_all(self):
        """Render every beat with no key handling. For CI / --render-all mode."""
        self._compute_layout()
        for bi in range(len(self.beats)):
            self._beat_idx = bi
            beat = self.beats[bi]
            if beat.get("prompt"):
                prefix = beat.get("prefix", "  > ")
                if self._line_buf and self._line_buf[-1] != "":
                    self._line_buf.append("")  # separator from the previous turn
                for pl in wrap_prompt_lines(prefix, beat["prompt"], self._left_w, self.color):
                    self._line_buf.append(pl)
                self._line_buf.append("")  # blank line between prompt and response
            # Fullscreen (vi) beats: surface the editor buffer in the headless
            # snapshot so coverage checks see its content (e.g. the masked auth).
            for text, _style in beat.get("fullscreen", []):
                self._line_buf.append(apply_color(text, _style, self.color))
            for frag in beat.get("fragments", []):
                for fline_text, _delay in fragment_to_lines(frag, self._left_w, self.color):
                    self._line_buf.append(fline_text)
            self._repaint(bi, self._line_buf, 0)

    # -------------------------------------------------------------------------
    # Interactive run loop
    # -------------------------------------------------------------------------
    def run(self, start=0):
        """Interactive arrow-driven run. Requires a real TTY."""
        self._setup_terminal()
        self._install_signals()

        # Enter alt screen, hide cursor, enable mouse scroll (X10 + SGR encoding)
        self._write_raw("\x1b[?1049h")
        self._write_raw("\x1b[?25l")
        self._write_raw("\x1b[?1000h")    # enable X10 mouse button events (scroll wheel)
        self._write_raw("\x1b[?1006h")    # use SGR encoding (better for larger terminals)

        try:
            self._compute_layout()
            self._beat_idx = start
            self._line_buf = self._rebuild_line_buf(start)
            self._scroll_offset = 0
            self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)

            while True:
                # Handle pending SIGWINCH
                if self._needs_repaint:
                    self._needs_repaint = False
                    self._compute_layout()
                    self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)

                key = self._read_key()
                if key == "QUIT":
                    break
                elif key == "RIGHT":
                    if self._in_fullscreen:
                        # vi ':wq' — exit the takeover, stream any post-edit
                        # fragments (usually none), advance to the next beat.
                        self._in_fullscreen = False
                        self._scroll_offset = 0
                        self._stream_beat_frags(self._beat_idx, self._line_buf)
                        self._beat_idx += 1
                        self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                    elif self._beat_idx < len(self.beats):
                        beat = self.beats[self._beat_idx]
                        if beat.get("prompt") and not self._half_beat:
                            # First press: type out the prompt character by character,
                            # wrapping inside the left pane (never off-screen).
                            prefix = beat.get("prefix", "  > ")
                            # 35ms per char regardless of speed (feels like fast human
                            # typing); instant at speed=0.
                            char_delay = 0 if self.speed <= 0 else 0.035
                            prompt_start = len(self._line_buf)
                            self._scroll_offset = 0
                            # Blank separator between the previous turn and this prompt.
                            lead = [""] if (self._line_buf and self._line_buf[-1] != "") else []

                            typed = ""
                            skip_typing = False
                            cancel_typing = False
                            self._line_buf[prompt_start:] = lead + wrap_prompt_lines(
                                prefix, "", self._left_w, self.color)
                            self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                            for ch in beat["prompt"]:
                                typed += ch
                                self._line_buf[prompt_start:] = lead + wrap_prompt_lines(
                                    prefix, typed, self._left_w, self.color)
                                self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                                if not skip_typing and char_delay > 0:
                                    if self._wait_ready(char_delay):
                                        k = self._read_key()
                                        if k == "QUIT":
                                            raise Quit()
                                        elif k == "RIGHT":
                                            skip_typing = True
                                        elif k == "LEFT":
                                            cancel_typing = True
                                            break

                            if cancel_typing:
                                del self._line_buf[prompt_start:]  # remove partial prompt
                                self._scroll_offset = 0
                                self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                                continue

                            # Ensure full prompt visible (skip_typing may have jumped out)
                            self._line_buf[prompt_start:] = lead + wrap_prompt_lines(
                                prefix, beat["prompt"], self._left_w, self.color)
                            self._line_buf.append("")  # blank line before response
                            self._half_beat = True
                            self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                        elif beat.get("fullscreen") and self._half_beat:
                            # Second press on a vi beat: open the editor takeover
                            # (clean full-pane view); the stream comes on the next press.
                            self._half_beat = False
                            self._in_fullscreen = True
                            self._scroll_offset = 0
                            self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                        else:
                            # Second press (or beat has no prompt): stream fragments
                            self._half_beat = False
                            self._scroll_offset = 0
                            self._stream_beat_frags(self._beat_idx, self._line_buf)
                            self._beat_idx += 1
                            self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                    else:
                        self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                elif key == "LEFT":
                    if self._in_fullscreen:
                        # Back out of vi without writing: drop the typed `vi ...`
                        # line and return to the clean pre-command shell state.
                        self._in_fullscreen = False
                        self._scroll_offset = 0
                        self._line_buf = self._rebuild_line_buf(self._beat_idx)
                        self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                    elif self._half_beat:
                        # Cancel the half-shown prompt. The prompt may have wrapped to
                        # several lines, so rebuild cleanly rather than popping a fixed count.
                        self._half_beat = False
                        self._scroll_offset = 0
                        self._line_buf = self._rebuild_line_buf(self._beat_idx)
                        self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                    else:
                        self._beat_idx = max(0, self._beat_idx - 1)
                        self._scroll_offset = 0
                        self._line_buf = self._rebuild_line_buf(self._beat_idx)
                        self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                elif key == "UP":
                    max_scroll = max(0, len(self._line_buf) - self._content_rows)
                    self._scroll_offset = min(max_scroll, self._scroll_offset + 3)
                    self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                elif key == "DOWN":
                    self._scroll_offset = max(0, self._scroll_offset - 3)
                    self._repaint(self._beat_idx, self._line_buf, self._scroll_offset)
                # ESC / NONE / IGNORE: do nothing

        except Quit:
            pass
        finally:
            self._restore()
            self._write_raw("\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _load():
    """Load beats and notes, inserting the player directory into sys.path."""
    player_dir = os.path.dirname(os.path.abspath(__file__))
    if player_dir not in sys.path:
        sys.path.insert(0, player_dir)
    from content import REPLAY_BEATS
    from notes import NOTES
    return REPLAY_BEATS, NOTES


def _selftest(beats, notes):
    """Quick integrity checks — called automatically at startup."""
    errors = []

    # Every beat must have a NOTES entry
    for beat in beats:
        lbl = beat["label"]
        if lbl not in notes:
            errors.append(f"NOTES missing entry for beat label: {lbl!r}")

    # The vi beat must NOT show a real credential
    for beat in beats:
        if beat.get("label") == "wire: open mcp.json in vi":
            import json as _json
            import re
            from engine import apply_color, fragment_to_lines
            frag_lines = []
            for frag in beat.get("fragments", []):
                frag_lines.extend(fragment_to_lines(frag, 120, color=False))
            rendered_parts = [line for line, _ in frag_lines]
            # The vi content now lives in the fullscreen buffer — check it too.
            rendered_parts += [text for text, _style in beat.get("fullscreen", [])]
            rendered = "\n".join(rendered_parts)
            # Must contain the masked placeholder
            if "‹redacted›" not in rendered:
                errors.append("wire beat: auth value must render as 'Basic ‹redacted›'")
            # Must NOT contain a real base64 API key (heuristic: long alphanum= string)
            real_key_pattern = re.compile(r'[A-Za-z0-9+/]{40,}={0,2}')
            if real_key_pattern.search(rendered):
                errors.append("wire beat: possible real credential found in rendered output")

    return errors


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Two-column replay player for the AWS Summit demo."
    )
    p.add_argument("--from-beat", type=int, default=0,
                   help="start at this beat index (see --list)")
    p.add_argument("--list", action="store_true",
                   help="print beat index -> act -> label map and exit")
    p.add_argument("--render-all", action="store_true",
                   help="auto-play every beat (no keys); pair with --speed 0 for instant")
    p.add_argument("--speed", type=float, default=0.25,
                   help="animation speed multiplier (0 = instant, default 0.25 = slow)")
    p.add_argument("--no-color", action="store_true",
                   help="disable ANSI color")
    args = p.parse_args(argv)

    beats, notes = _load()

    # Self-test on every run
    errors = _selftest(beats, notes)
    if errors:
        for e in errors:
            sys.stderr.write(f"SELFTEST FAIL: {e}\n")
        return 2

    if args.list:
        for i, b in enumerate(beats):
            print(f"{i:>4}  {b['act']:<30} {b['label']}")
        return 0

    color = not args.no_color
    player = ReplayPlayer(beats, notes, color=color, speed=args.speed,
                          render_all_mode=args.render_all)

    if args.render_all:
        player.render_all()
        return 0

    if not sys.stdin.isatty():
        sys.stderr.write(
            "replay.py needs a TTY for interactive mode. Use --render-all in a pipe.\n"
        )
        return 2

    player.run(start=args.from_beat)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
