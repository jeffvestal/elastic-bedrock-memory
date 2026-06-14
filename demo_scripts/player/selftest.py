"""
Automated verification harness for the demo player. No TTY, no network.

Run:  python3 demo_scripts/player/selftest.py
Exits 0 if all checks pass, 1 otherwise. Each check prints PASS / FAIL / SKIP.

Covers what can be verified without a human at the keyboard:
  schema, render smoke, two-press structure, act-contrast invariants, verbatim
  fidelity (Act 2/3), Act 1 gap fidelity, key decoding (incl. lone-ESC no-hang),
  fast-forward drain (drain-not-finish), terminal-restore sanity, no-rich render,
  and a real-terminal PTY smoke test (exercises cbreak/termios + the key loop).
"""
import os
import select
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import play  # noqa: E402
import content  # noqa: E402

KNOWN_FRAGS = {
    "line", "blank", "rule", "tool", "toolline", "write", "code",
    "footer", "banner", "status", "idle", "sessionend",
}


def render(steps):
    """Instant, plain-text render of a step list -> captured string."""
    buf = []
    play.Player(steps, out=buf.append, color=False, speed=0).render_all()
    return "".join(buf)


class FakeKeys:
    """Scripted key source for decode_key (no termios)."""
    def __init__(self, data):
        self.data = data
        self.i = 0

    def read_byte(self):
        if self.i >= len(self.data):
            return ""
        ch = self.data[self.i]
        self.i += 1
        return ch

    def wait_ready(self, timeout):
        return self.i < len(self.data)


# ---------------------------------------------------------------------------
# Checks. Each returns (ok: bool, detail: str) or raises (treated as FAIL).
# A check may return ("SKIP", detail) to skip.
# ---------------------------------------------------------------------------
def check_schema():
    for i, s in enumerate(content.STEPS):
        kind = s.get("kind")
        if kind not in ("input", "stream", "instant"):
            return False, f"step {i}: bad kind {kind!r}"
        if kind == "input" and not isinstance(s.get("text"), str):
            return False, f"step {i}: input missing text"
        if kind in ("stream", "instant"):
            frags = s.get("fragments")
            if not isinstance(frags, list):
                return False, f"step {i}: {kind} missing fragments list"
            for f in frags:
                if not isinstance(f, dict) or f.get("t") not in KNOWN_FRAGS:
                    return False, f"step {i}: unknown fragment {f!r}"
    return True, f"{len(content.STEPS)} steps valid"


def check_render_smoke():
    for i, s in enumerate(content.STEPS):
        out = render([s])
        if not out:
            return False, f"step {i} ({s.get('label') or s['kind']}) rendered empty"
    full = render(content.STEPS)
    return True, f"all steps render; full output {len(full)} chars"


def check_two_press_structure():
    steps = content.STEPS
    for i, s in enumerate(steps):
        if s["kind"] == "input":
            if i + 1 >= len(steps) or steps[i + 1]["kind"] != "stream":
                return False, f"input step {i} ({s.get('label')}) not followed by a stream"
    return True, "every input is followed by a stream (two-press turn)"


def check_act_contrast():
    a1 = render(content.SEGMENTS["act1"])
    a2 = render(content.SEGMENTS["act2"])
    a3 = render(content.SEGMENTS["act3"])
    if "search-knowledge-facts" in a1:
        return False, "Act 1 must NOT call search-knowledge-facts (it's the amnesiac contrast)"
    if "search-knowledge-facts" not in a2:
        return False, "Act 2 must call search-knowledge-facts"
    if "save-knowledge-fact" not in a2:
        return False, "Act 2 must call save-knowledge-fact (write beat)"
    for fn in ("app/models.py", "app/payments.py", "app/routers/checkout.py"):
        if fn not in a2:
            return False, f"Act 2 must write {fn}"
    if "search-knowledge-facts" not in a3:
        return False, "Act 3 must call search-knowledge-facts (read-back)"
    return True, "Act 1 silent; Act 2 search+save+3 writes; Act 3 search"


def check_verbatim_fidelity():
    combined = render(content.SEGMENTS["act2"]) + render(content.SEGMENTS["act3"])
    tokens = [
        "sess-004-fact-2", "sess-005-fact-0", "sess-007-fact-0", "Wn9ktp4B",
        "refund-{order_id}-{refund_cents}", "refund-{uuid.uuid4()}", "▸ Credits",
    ]
    missing = [t for t in tokens if t not in combined]
    if missing:
        return False, f"missing verbatim tokens: {missing}"
    return True, "all Act 2/3 verbatim tokens present"


def check_act1_gaps():
    a1 = render(content.SEGMENTS["act1"])
    if "{order_id}-refund-{amount_cents}" not in a1:
        return False, "Act 1 should ship the amount-based idempotency key"
    forbidden = ["90-day", "90 days", "prior refund", "capped", "refund window"]
    leaked = [p for p in forbidden if p.lower() in a1.lower()]
    if leaked:
        return False, f"Act 1 leaked a policy it can't know: {leaked}"
    return True, "Act 1 ships amount-based key; no policy leakage"


def check_key_decoder():
    cases = {
        "\x1b[C": "RIGHT",
        "\x1b[D": "LEFT",
        "\x1b[A": "UP",
        "\x1bOC": "RIGHT",
        "q": "QUIT",
        "\x03": "QUIT",
    }
    for data, want in cases.items():
        fk = FakeKeys(data)
        got = play.decode_key(fk.read_byte, fk.wait_ready)
        if got != want:
            return False, f"decode({data!r}) -> {got}, want {want}"
    # lone ESC: must return ESC without consuming a (nonexistent) tail and without hanging
    fk = FakeKeys("\x1b")
    got = play.decode_key(fk.read_byte, fk.wait_ready)
    if got != "ESC":
        return False, f"lone ESC -> {got}, want ESC"
    if fk.i != 1:
        return False, f"lone ESC over-read {fk.i} bytes (would block on a real fd)"
    return True, "arrows, q, Ctrl-C, application-mode, and lone-ESC all decode correctly"


def check_fastforward_drain():
    # Pick a representative stream step (the write-beat response).
    step = None
    for s in content.SEGMENTS["act2"]:
        if s["kind"] == "stream" and s.get("label", "").startswith("response: Act 2 — write beat"):
            step = s
            break
    if step is None:
        return False, "could not find the write-beat stream step"

    full = render([step])  # instant full render = ground truth

    # Drain: real delays, but a RIGHT arrives at the first delay -> skip=True.
    buf = []
    p = play.Player([step], out=buf.append, color=False, speed=1.0)
    p._wait_ready = lambda t: True       # a key is always "ready" during a delay
    p.read_key = lambda: "RIGHT"          # ...and it's a fast-forward
    p.play_step(step, interactive=True)
    drained = "".join(buf)

    if drained != full:
        return False, "fast-forward dropped output (drain != full render)"
    return True, "fast-forward drains all remaining output (drain-not-finish)"


def check_restore_sanity():
    p = play.Player(content.STEPS, out=lambda s: None)
    # restore with nothing saved must be a harmless no-op (idempotent).
    p.restore_terminal()
    p.restore_terminal()
    return True, "restore_terminal() is idempotent / no-throw"


def check_no_rich():
    # We intentionally render code blocks plain (matches Kiro) — no rich dependency.
    if "rich" in sys.modules:
        return False, "play.py pulled in 'rich' (should render code plain, no dependency)"
    out = render([play.step_stream([play.code(["import uuid", "x = 1"])])])
    if "import uuid" not in out:
        return False, "code() fragment did not render its lines"
    return True, "code renders plain; no rich dependency"


def check_pty_smoke():
    try:
        import pty
        import threading
        master, slave = pty.openpty()
    except OSError as e:
        return "SKIP", f"pty unavailable: {e}"

    play_path = os.path.join(HERE, "play.py")
    proc = subprocess.Popen(
        [sys.executable, play_path, "--speed", "80"],
        stdin=slave, stdout=slave, stderr=slave, close_fds=True,
    )
    os.close(slave)

    # Drain the master CONTINUOUSLY on a thread so the child never blocks on a
    # full pty output buffer (that backpressure would look like a hang).
    captured = bytearray()
    stop = threading.Event()

    def reader():
        while not stop.is_set():
            try:
                r, _, _ = select.select([master], [], [], 0.1)
                if r:
                    b = os.read(master, 4096)
                    if not b:
                        break
                    captured.extend(b)
            except OSError:
                break

    th = threading.Thread(target=reader, daemon=True)
    th.start()

    # 6 RIGHTs advance through launch + Act 1 into the live-build; then a lone ESC
    # (must be ignored, not hang), then q to quit.
    seq = [b"\x1b[C"] * 6 + [b"\x1b", b"q"]
    rc = None
    try:
        for k in seq:
            try:
                os.write(master, k)
            except OSError:
                break
            time.sleep(0.35)
        try:
            rc = proc.wait(timeout=6)
        except subprocess.TimeoutExpired:
            proc.kill()
            rc = None
    finally:
        stop.set()
        try:
            os.close(master)
        except OSError:
            pass
        th.join(timeout=1)

    out = bytes(captured)
    if rc is None:
        return False, "player did not exit after lone-ESC + q (possible hang)"
    if rc != 0:
        return False, f"player exited rc={rc}"
    if b"kiro-cli" not in out:
        return False, "expected 'kiro-cli' in PTY output"
    advanced = b"Creating indices" in out
    return True, f"spawned in pty, lone-ESC ignored, clean exit (advanced_to_livebuild={advanced})"


CHECKS = [
    ("1  import & schema", check_schema),
    ("2  render smoke", check_render_smoke),
    ("3  two-press structure", check_two_press_structure),
    ("4  act-contrast invariants", check_act_contrast),
    ("5  verbatim fidelity (Act 2/3)", check_verbatim_fidelity),
    ("6  Act 1 gap fidelity", check_act1_gaps),
    ("7  key decoder (+ lone-ESC)", check_key_decoder),
    ("8  fast-forward drain", check_fastforward_drain),
    ("9  terminal-restore sanity", check_restore_sanity),
    ("10 no-rich plain code", check_no_rich),
    ("11 PTY smoke (real terminal)", check_pty_smoke),
]


def main():
    print("\n=== demo player — self-verification ===\n")
    failures = 0
    skips = 0
    for name, fn in CHECKS:
        try:
            res = fn()
            ok, detail = res
        except Exception as e:  # a check that throws is a failure
            ok, detail = False, f"raised {type(e).__name__}: {e}"
        if ok == "SKIP":
            print(f"  SKIP  {name}  — {detail}")
            skips += 1
        elif ok:
            print(f"  PASS  {name}  — {detail}")
        else:
            print(f"  FAIL  {name}  — {detail}")
            failures += 1
    total = len(CHECKS)
    print(f"\n  {total - failures - skips}/{total} passed, {failures} failed, {skips} skipped\n")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
