#!/usr/bin/env python3
"""Shim so `python3 tracker.py <args>` runs tracker.cli from the repo root."""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tracker.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
