"""
engine.py — shared core for the demo player (classic and split/replay).

Exports:
  Palette, timing constants, KIRO_BANNER/BANNER_WELCOME
  Quit exception
  Fragment factories: line, blank, rule, tool, toolline, write, code, footer, banner,
                      status, idle, sessionend, permbreak, mcpbreak, thinking
  Step factories: step_input, step_stream, step_instant
  decode_key(read_byte, wait_ready) -> key name
  apply_color(s, style, enabled, palette) -> styled string
  fragment_to_lines(frag, width, color=True) -> list of (styled_line_no_newline, delay)
"""
from __future__ import annotations

import select

# ---------------------------------------------------------------------------
# Palette (truecolor). Tunable — match a Kiro screenshot for pixel-perfect hue.
# ---------------------------------------------------------------------------
RESET = "\x1b[0m"
PALETTE = {
    "dim":     "\x1b[38;2;128;132;140m",   # dim gray (args, footer, hints)
    "tool":    "\x1b[38;2;86;204;180m",     # teal — the ● tool-call dot
    "user":    "\x1b[38;2;235;236;238m",    # near-white — typed user input
    "text":    "\x1b[0m",                    # default fg — Kiro prose
    "green":   "\x1b[38;2;126;199;130m",    # diff +
    "red":     "\x1b[38;2;224;108;117m",     # diff -
    "rule":    "\x1b[38;2;88;92;100m",       # box-drawing rules
    "accent":  "\x1b[38;2;126;199;130m",     # ● confirmations / Good catch
    "banner":  "\x1b[38;2;134;90;230m",      # purple-ish Kiro logo
    "status":  "\x1b[38;2;128;132;140m",     # bottom status line
    "bold":    "\x1b[1m",
    # Right-pane commentary colors
    "headline": "\x1b[38;2;86;204;180m\x1b[1m",  # teal+bold — beat headline
    "bullet":   "\x1b[38;2;235;236;238m",          # near-white bullets
    "emph":     "\x1b[38;2;126;199;130m",           # green — key terms
}

# Animation timing (seconds, before --speed scaling). speed==0 => instant.
T_CHAR = 0.028     # per character when typing input
T_WORD = 0.040     # per word-chunk when streaming prose
T_LINE = 0.077     # per structural line (tool calls, diffs, etc.)
T_TOOL = 0.25      # extra beat after a tool-call line (let it land)
T_GAP = 0.17       # small beat between major fragments
ESC_TIMEOUT = 0.06  # seconds to wait for an escape-sequence tail after ESC

KIRO_BANNER = r"""                      ⢀⣴⣶⣶⣦⡀⠀⠀⠀⠀⢀⣴⣶⣦⣄⡀   ⢀⣴⣶⣶⣦⡀   ⢀⣴⣶⣶⣶⣶⣶⣶⣶⣶⣶⣦⣄⡀       ⢀⣠⣴⣶⣶⣶⣶⣶⣦⣄⡀
                     ⢰⣿⠋⠁⠈⠙⣿⡆⠀⢀⣾⡿⠁  ⠈⢻⡆ ⢰⣿⠋⠁⠈⠙⣿⡆ ⢰⣿⠋⠁        ⠈⠙⠻⣦     ⣴⡿⠟⠋⠁   ⠈⠙⠻⢿⣦
                     ⢸⣿⠀⠀⠀⠀⣿⣇⣴⡿⠋⠀⠀  ⢀⣼⠇ ⢸⣿⠀⠀⠀⠀⣿⡇ ⢸⣿⠀⠀⠀⢠⣤⣤⣤⣤⣄    ⣿⡆   ⣼⡟⠀⠀⠀ ⣀⣀⣀    ⢻⣧
                     ⢸⣿⠀⠀⠀⠀⣿⡿⠋⠀⠀  ⢀⣾⡿⠁  ⢸⣿⠀⠀⠀⠀⣿⡇ ⢸⣿⠀⠀⠀⢸⣿⠉⠉⠉⣿⡇   ⣿⡇  ⣼⡟⠀⠀ ⣰⡿⠟⠛⠻⢿⣆⠀⠀ ⢻⣧
                     ⢸⣿⠀⠀⠀⠀⠙⠁⠀⠀ ⢀⣼⡟⠁    ⢸⣿⠀⠀⠀⠀⣿⡇ ⢸⣿⠀⠀⠀⢸⣿⣶⣶⡶⠋⠀   ⣿⠇ ⢰⣿⠀⠀⠀⢰⣿⠀⠀⠀  ⣿⡆⠀⠀ ⣿⡆
                     ⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀ ⠹⣷⡀     ⢸⣿⠀⠀⠀⠀⣿⡇⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀   ⣠⣼⠟  ⢸⣿⠀⠀ ⢸⣿⠀⠀⠀⠀ ⣿⡇⠀⠀ ⣿⡇
                     ⢸⣿⠀⠀⠀⠀⠀⣠⡀⠀⠀ ⠹⣷⡄    ⢸⣿⠀⠀⠀⠀⣿⡇⠀⢸⣿⠀⠀⠀⠀⣤⣄  ⠀⠀⠹⣿⡅   ⠸⣿⠀⠀ ⠸⣿⠀⠀⠀⠀ ⣿⠇⠀  ⣿⠇
                     ⢸⣿⠀⠀⠀⠀⣾⡟⣷⡀⠀⠀ ⠘⣿⣆   ⢸⣿⠀⠀⠀⠀⣿⡇ ⢸⣿⠀⠀⠀⠀⣿⡟⣷⡀⠀⠀ ⠘⣿⣆   ⢻⣧⠀⠀ ⠹⣷⣦⣤⣤⣾⠏⠀⠀⠀⣼⡟
                     ⢸⣿⠀⠀⠀⠀⣿⡇⠹⣷⡀  ⠀⠈⢻⡇  ⢸⣿⠀⠀⠀⠀⣿⡇ ⢸⣿⠀⠀⠀⠀⣿⡇⠹⣷⡀  ⠀⠈⢻⡇   ⢻⣧⠀⠀⠀ ⠉⠉⠉    ⣼⡟
                     ⠸⣿⣄⡀⢀⣠⣿⠇⠀⠙⣷⡀  ⢀⣼⠇  ⠸⣿⣄⡀⢀⣠⣿⠇ ⠸⣿⣄⡀⢀⣠⣿⠇⠀⠙⣷⡀  ⢀⣼⠇    ⠻⣷⣦⣄⡀   ⢀⣠⣴⣾⠟
                      ⠈⠻⠿⠿⠟⠁⠀⠀⠀⠈⠻⠿⠿⠟⠁    ⠈⠻⠿⠿⠟⠁   ⠈⠻⠿⠿⠟⠁⠀⠀⠀⠈⠻⠿⠿⠟⠁     ⠀⠀⠈⠙⠻⠿⠿⠿⠿⠟⠋⠁"""

BANNER_WELCOME = [
    "",
    "                Welcome to the new Kiro CLI UX! /tui to learn more, /feedback for thoughts.",
    "                     Prefer the classic experience? Relaunch with kiro-cli --classic.",
]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
class Quit(Exception):
    pass


# ---------------------------------------------------------------------------
# Color helper
# ---------------------------------------------------------------------------
def apply_color(s, style, enabled=True):
    """Apply a palette style to s. Returns plain s when disabled or style not found."""
    if not enabled or not style:
        return s
    code = PALETTE.get(style, "")
    return f"{code}{s}{RESET}" if code else s


# ---------------------------------------------------------------------------
# Fragment factories — the vocabulary content.py composes with.
# Each returns a plain dict so content is pure data and trivially serializable.
# ---------------------------------------------------------------------------
def line(s="", indent=2, style="text", stream=True):
    """A prose line. stream=True types it in word-chunks; False emits whole."""
    return {"t": "line", "s": s, "indent": indent, "style": style, "stream": stream}


def blank():
    return {"t": "blank"}


def rule():
    return {"t": "rule"}


def tool(name, arg=None):
    """Kiro tool call: '● name' with optional '    ╰ arg' sub-line."""
    return {"t": "tool", "name": name, "arg": arg}


def toolline(label, detail=None):
    """Generic '● label' line (e.g. Read /path) with optional dim detail sub-line."""
    return {"t": "toolline", "label": label, "detail": detail}


def write(path, summary, diff=None):
    """File-write block: '● Write /path', a summary line, then a colored diff."""
    return {"t": "write", "path": path, "summary": summary, "diff": diff or []}


def code(lines, indent=2):
    """Fenced code block. Kiro renders these plain/dim; we match that."""
    return {"t": "code", "lines": lines, "indent": indent}


def footer(credits, time):
    return {"t": "footer", "credits": credits, "time": time}


def banner():
    return {"t": "banner"}


def status(agent, model="auto", ctx="◔ 3%", cwd="~/repos/checkout-service-demo", branch="main"):
    return {"t": "status", "agent": agent, "model": model, "ctx": ctx, "cwd": cwd, "branch": branch}


def idle():
    """The idle input box hint Kiro shows when waiting for a prompt."""
    return {"t": "idle"}


def sessionend(resume):
    return {"t": "sessionend", "resume": resume}


def permbreak(path, scope="app", stage="both"):
    """Write-approval dialog — rendered before the first granted write in a session.
    stage: 'trust' (first dialog only), 'scope' (second dialog only), or 'both'
    (default). The replay player pauses after each staged dialog so the presenter
    arrows through every approval."""
    return {"t": "permbreak", "path": path, "scope": scope, "stage": stage}


def mcpbreak(tool_name):
    """MCP read-tool first-use approval dialog — real Kiro shows this before the
    first call to each MCP tool. Pauses the replay player so the presenter arrows
    through the approval. Order differs from permbreak: 'Yes, single permission'
    is highlighted first (matching Image #11 screenshot)."""
    return {"t": "mcpbreak", "tool_name": tool_name}


def thinking():
    """Kiro 'Thinking...' indicator shown while the agent processes tool results."""
    return {"t": "thinking"}


# ---------------------------------------------------------------------------
# Step factories.
# ---------------------------------------------------------------------------
def step_input(text, prefix="  ", label=None, auto=False):
    """Types `text` after `prefix` (no newline — waits for the 'enter' press)."""
    return {"kind": "input", "text": text, "prefix": prefix, "label": label, "auto": auto}


def step_stream(fragments, label=None, auto=False):
    """Emits the newline (enter), then streams `fragments`."""
    return {"kind": "stream", "fragments": fragments, "label": label, "auto": auto}


def step_instant(fragments, label=None, auto=True):
    """Renders `fragments` with no animation (banner, idle box, rules)."""
    return {"kind": "instant", "fragments": fragments, "label": label, "auto": auto}


# ---------------------------------------------------------------------------
# Key decoding — standalone + fully testable (no termios needed).
#   read_byte()        -> next 1-char string ("" if none)
#   wait_ready(timeout)-> True if more input is available within timeout
# Returns one of: RIGHT LEFT UP DOWN QUIT ESC NONE IGNORE
# ---------------------------------------------------------------------------
def decode_key(read_byte, wait_ready):
    b = read_byte()
    if b == "":
        return "NONE"
    if b in ("q", "Q", "\x03", "\x04"):
        return "QUIT"
    if b == "\x1b":
        # ESC-disambiguation: a lone ESC must NOT block waiting for a tail.
        if not wait_ready(ESC_TIMEOUT):
            return "ESC"
        b2 = read_byte()
        if b2 in ("[", "O"):  # CSI or application-cursor mode
            b3 = read_byte()
            return {"C": "RIGHT", "D": "LEFT", "A": "UP", "B": "DOWN"}.get(b3, "IGNORE")
        return "IGNORE"
    return "IGNORE"


# ---------------------------------------------------------------------------
# Diff line helper (shared between classic and replay)
# ---------------------------------------------------------------------------
def diff_line(sign, lineno, content, color=True):
    num = f"{lineno:>4}" if lineno != "" else "    "
    if sign == "+":
        return apply_color(f"  {num}{sign}  {content}", "green", color)
    if sign == "-":
        return apply_color(f"  {num}{sign}  {content}", "red", color)
    return apply_color(f"  {num}   {content}", "dim", color)


# ---------------------------------------------------------------------------
# fragment_to_lines — width-aware, returns complete styled lines (no \n).
# Used by the replay compositor's line buffer and the right-pane note renderer.
# Returns list of (styled_string, delay).
# ---------------------------------------------------------------------------
def fragment_to_lines(frag, width, color=True):
    """
    Render a fragment into a list of (styled_line_no_newline, delay) tuples.
    Each string is a complete line — no embedded newlines.
    Wraps to `width` using the same hanging-indent algorithm as play_classic.
    """
    c = lambda s, style: apply_color(s, style, color)
    t = frag["t"]

    if t == "blank":
        return [("", 0.0)]

    elif t == "rule":
        return [(c("─" * max(1, width), "rule"), T_LINE)]

    elif t == "line":
        indent = " " * frag.get("indent", 2)
        style = frag.get("style", "text")
        s = frag["s"]
        if not s:
            return [(indent, 0.0)]
        maxw = max(20, width)
        # Word-wrap with hanging indent — same algorithm as classic iter_fragment.
        result_lines = []
        col = len(indent)
        current = indent
        words = s.split(" ")
        for i, w in enumerate(words):
            if col + len(w) > maxw and col > len(indent):
                result_lines.append(c(current, style))
                current = indent
                col = len(indent)
            last = (i == len(words) - 1)
            current += w if last else w + " "
            col += len(w) + (0 if last else 1)
        if current != indent:
            result_lines.append(c(current.rstrip(), style))
        return [(ln, T_WORD) for ln in result_lines] if result_lines else [("", 0.0)]

    elif t == "tool":
        dot = c("●", "tool")
        result = [(f"{dot} {c(frag['name'], 'tool')}", T_LINE)]
        if frag.get("arg"):
            result.append((c(f"    ╰ {frag['arg']}", "dim"), T_TOOL))
        else:
            result.append(("", T_TOOL))
        return result

    elif t == "toolline":
        dot = c("●", "tool")
        label = frag["label"]
        # Color path segments (anything starting with /) in teal, matching real Kiro
        parts = label.split(" ", 1)
        if len(parts) == 2 and parts[1].startswith("/"):
            label_rendered = parts[0] + " " + c(parts[1], "tool")
        else:
            label_rendered = label
        result = [(f"{dot} {label_rendered}", T_LINE)]
        if frag.get("detail"):
            result.append((c(f"    {frag['detail']}", "dim"), T_TOOL))
        else:
            result.append(("", T_TOOL))
        return result

    elif t == "write":
        dot = c("●", "tool")
        result = [(f"{dot} {c('Write', 'tool')} {frag['path']}", T_LINE)]
        result.append((c("  " + frag["summary"], "dim"), T_LINE))
        for sign, lineno, content in frag["diff"]:
            result.append((diff_line(sign, lineno, content, color), T_LINE))
        result.append(("", T_GAP))
        return result

    elif t == "code":
        indent = " " * frag.get("indent", 2)
        result = [(c(indent + ln, "dim"), T_LINE) for ln in frag["lines"]]
        result.append(("", T_GAP))
        return result

    elif t == "footer":
        txt = f"▸ Credits: {frag['credits']} • Time: {frag['time']}"
        return [("", 0.0), (c(txt, "dim"), T_GAP)]

    elif t == "banner":
        result = []
        for banner_line in KIRO_BANNER.split("\n"):
            result.append((c(banner_line, "banner"), 0.0))
        for wl in BANNER_WELCOME:
            result.append((c(wl, "dim"), 0.0))
        return result

    elif t == "status":
        w = width
        left = f"  {frag['agent']} · {frag['model']} · {frag['ctx']}"
        right = f"{frag['cwd']} · ({frag['branch']})  "
        pad = max(1, w - len(left) - len(right))
        return [(c(left + " " * pad + right, "status"), 0.0)]

    elif t == "idle":
        return [
            (c("  ask a question or describe a task ↵", "dim"), 0.0),
            (c("  Press Ctrl+C or Ctrl+D again to exit", "dim"), 0.0),
        ]

    elif t == "sessionend":
        return [
            ("", 0.0),
            ("", 0.0),
            ("", 0.0),
            (c("Session ended.", "dim"), 0.0),
            (c(f"Resume with: kiro-cli --resume-id {frag['resume']}", "dim"), 0.0),
            ("", 0.0),
            ("", 0.0),
            ("", 0.0),
        ]

    elif t == "permbreak":
        path = frag.get("path", "")
        scope = frag.get("scope", "app")
        stage = frag.get("stage", "both")
        short = path.split("/")[-1] if "/" in path else path
        trust = [
            (c("  write requires approval", "dim"), T_LINE),
            (c("  ▶ Trust, always allow in this session", "accent"), T_LINE),
            (c("    Yes, single permission", "dim"), 0.0),
            (c("    No (Tab to edit)", "dim"), 0.0),
            ("", T_GAP),
        ]
        scope_dialog = [
            (c("  write requires approval · trust options", "dim"), T_LINE),
            (c(f"  ▶ Complete directory   {scope}", "accent"), T_LINE),
            (c(f"    Specific paths       {short}", "dim"), 0.0),
            (c("    Entire tool", "dim"), 0.0),
            ("", T_GAP),
            (c("  ESC to close · Tab to edit", "dim"), T_GAP),
            ("", 0.0),
        ]
        if stage == "trust":
            return trust
        if stage == "scope":
            return scope_dialog
        return trust + scope_dialog

    elif t == "mcpbreak":
        tool_name = frag.get("tool_name", "mcp-tool")
        return [
            (c(f"  {tool_name} requires approval", "dim"), T_LINE),
            (c("  ❯ Yes, single permission", "banner"), T_LINE),
            (c("    Trust, always allow in this session", "dim"), 0.0),
            (c("    No (Tab to edit)", "dim"), 0.0),
            ("", T_GAP),
            (c("  ESC to close | Tab to edit", "dim"), T_GAP),
            ("", 0.0),
        ]

    elif t == "thinking":
        return [(c("≡ Thinking... (esc to cancel)", "dim"), T_TOOL)]

    else:
        return [(f"[unknown fragment: {t}]", 0.0)]
