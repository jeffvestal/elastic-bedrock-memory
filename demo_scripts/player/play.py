"""
play.py — compatibility shim. Re-exports everything from engine + play_classic.

Exists so that:
  - `from play import line, blank, ...`  (legacy content.py imports) still works.
  - `import play; play.decode_key(...)` (selftest) still works.
  - Any muscle-memory `python3 play.py` invocation still works (runs play_classic.main).

Delete this file once content.py and selftest.py have been updated to import from
engine / play_classic directly.
"""
from engine import *                          # palette, timing, factories, decode_key, Quit
from play_classic import Player               # the classic interactive player
from play_classic import main as _main        # for direct invocation

import sys as _sys
if __name__ == "__main__":
    raise SystemExit(_main())
